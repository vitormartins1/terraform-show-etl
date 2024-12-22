import json
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)


# Funções utilitárias

def clean_dict(obj: Any) -> Any:
    """
    Remove valores nulos, listas vazias e objetos vazios de dicionários ou listas.
    """
    if isinstance(obj, dict):
        return {k: clean_dict(v) for k, v in obj.items() if v}
    elif isinstance(obj, list):
        return [clean_dict(v) for v in obj if v]
    return obj


def normalize_reference(reference: str) -> str:
    """
    Normaliza a referência para usar apenas o nome base do recurso.
    - Para recursos 'managed': 'aws_instance.example.id' -> 'aws_instance.example'
    - Para recursos 'data': 'data.aws_ssm_parameter.example_param' -> 'data.aws_ssm_parameter.example_param'
    """
    parts = reference.split(".")
    if parts[0] == "data":
        # Para recursos 'data', usar as três primeiras partes
        return ".".join(parts[:3])
    else:
        # Para recursos 'managed', usar as duas primeiras partes
        return ".".join(parts[:2])


def deduplicate_relationships(relationships: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Remove relacionamentos duplicados com base nas referências normalizadas.
    """
    seen = set()
    unique_relationships = []
    for rel in relationships:
        # Normalizar 'from' e 'to' para deduplicação
        normalized_from = normalize_reference(rel["from"])
        normalized_to = normalize_reference(rel["to"])
        key = (normalized_from, normalized_to, rel["type"])

        if key not in seen:
            seen.add(key)
            unique_relationships.append({
                "from": normalized_from,
                "to": normalized_to,
                "type": rel["type"]
            })
    return unique_relationships


# Funções principais

def extract_metadata(terraform_json: Dict[str, Any]) -> Dict[str, str]:
    """
    Extrai metadados globais da configuração.
    """
    provider_config = terraform_json.get("configuration", {}).get("provider_config", {})
    return {
        "provider": next(iter(provider_config), "unknown"),
        "region": provider_config.get("aws", {}).get("expressions", {}).get("region", {}).get("constant_value", "unknown")
    }


def extract_resources(terraform_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrai recursos definidos na configuração do Terraform.
    """
    resources = terraform_json.get("configuration", {}).get("root_module", {}).get("resources", [])
    if not resources:
        logging.info("No resources found in the Terraform configuration.")
    return [clean_dict(resource) for resource in resources]


def extract_relationships(resources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Cria uma lista de relacionamentos com base nos recursos.
    """
    relationships = []
    for resource in resources:
        resource_name = resource.get("address")
        depends_on = resource.get("depends_on", [])
        expressions = resource.get("expressions", {})

        # Adicionar dependências explícitas
        for dependency in depends_on:
            relationships.append({
                "from": resource_name,
                "to": dependency,
                "type": "depends_on"
            })

        # Adicionar referências implícitas
        for value in expressions.values():
            if isinstance(value, dict) and "references" in value:
                for ref in value["references"]:
                    relationships.append({
                        "from": resource_name,
                        "to": ref,
                        "type": "reference"
                    })

    # Normalizar e deduplicar os relacionamentos
    return deduplicate_relationships(relationships)


def organize_resources_by_mode(resources: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Organiza os recursos por modo (managed/data) e tipo.
    """
    organized = {"managed": {}, "data": {}}

    for resource in resources:
        resource_mode = resource.get("mode", "managed")  # Padrão como managed
        resource_type = resource.get("type", "unknown")

        if resource_mode not in organized:
            organized[resource_mode] = {}

        if resource_type not in organized[resource_mode]:
            organized[resource_mode][resource_type] = []

        organized[resource_mode][resource_type].append(resource)

    return organized


def clean_resources(resources: Dict[str, List[Dict[str, Any]]], remove_references=True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Limpa recursos removendo campos desnecessários, propriedades vazias e referências após criar relacionamentos.
    """
    for resource_group in resources.values():
        for resource in resource_group:
            resource.pop("type", None)
            resource.pop("provider_config_key", None)
            resource.pop("schema_version", None)

            # Remover referências após extrair relacionamentos
            if remove_references:
                expressions = resource.get("expressions", {})
                for key in list(expressions.keys()):
                    if "references" in expressions[key]:
                        del expressions[key]

    return {k: [clean_dict(r) for r in v] for k, v in resources.items()}


# Pipeline de processamento

def process_terraform(terraform_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pipeline principal de processamento do Terraform JSON.
    """
    metadata = extract_metadata(terraform_json)
    raw_resources = extract_resources(terraform_json)
    relationships = extract_relationships(raw_resources)
    organized_resources = organize_resources_by_mode(raw_resources)
    cleaned_resources = {
        mode: clean_resources(resources, remove_references=(mode == "managed"))
        for mode, resources in organized_resources.items()
    }

    return {
        "metadata": metadata,
        "resources": cleaned_resources,
        "relationships": relationships
    }


# Função principal

def main():
    input_file = "terraform/terraform_state.json"
    output_file = "c4_deployment_data.json"

    # Carregar o JSON do Terraform
    with open(input_file, "r") as file:
        terraform_data = json.load(file)

    # Processar dados
    final_data = process_terraform(terraform_data)

    # Salvar dados processados
    with open(output_file, "w") as outfile:
        json.dump(final_data, outfile, indent=2)

    logging.info(f"Deployment data saved to '{output_file}'")


if __name__ == "__main__":
    main()