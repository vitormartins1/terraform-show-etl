import json

def remove_empty_values(obj):
    """Remove valores nulos, listas vazias e objetos vazios de dicionários ou listas."""
    if isinstance(obj, dict):
        return {
            k: remove_empty_values(v)
            for k, v in obj.items()
            if v is not None and (not isinstance(v, (dict, list)) or v)
        }
    elif isinstance(obj, list):
        return [remove_empty_values(v) for v in obj if v is not None and (not isinstance(v, (dict, list)) or v)]
    else:
        return obj

def extract_metadata(terraform_json):
    """Extrai metadados globais da configuração."""
    provider_config = terraform_json.get("configuration", {}).get("provider_config", {})
    return {
        "provider": list(provider_config.keys())[0] if provider_config else "unknown",
        "region": provider_config.get("aws", {}).get("expressions", {}).get("region", {}).get("constant_value", "unknown")
    }

def remove_unnecessary_fields(resources):
    """
    Remove o campo 'type' de cada recurso dentro de cada grupo após o agrupamento.
    """
    for resource_group in resources.values():
        for resource in resource_group:
            resource.pop("type", None) 
            resource.pop("provider_config_key", None)
            resource.pop("schema_version", None)
    return resources

def organize_resources_by_type(resources):
    """Organiza os recursos extraídos por tipo."""
    organized = {}
    for resource in resources:
        resource_type = resource.get("type")
        if resource_type not in organized:
            organized[resource_type] = []
        organized[resource_type].append(resource)

    return remove_unnecessary_fields(organized)

def normalize_reference(ref):
    """
    Normaliza uma referência para usar apenas o nome do recurso,
    que consiste nas duas primeiras partes separadas por ponto.
    """
    parts = ref.split(".")
    return ".".join(parts[:2])  # Retorna apenas as duas primeiras partes

def deduplicate_relationships(relationships):
    """
    Remove relacionamentos redundantes com base nas referências normalizadas.
    Classifica o tipo como 'reference' ou 'depends_on'.
    """
    deduplicated = {}
    for rel in relationships:
        # Normaliza as referências `from` e `to`
        normalized_from = normalize_reference(rel["from"])
        normalized_to = normalize_reference(rel["to"])
        key = (normalized_from, normalized_to)

        # Sempre classifica o tipo em 'reference' ou 'depends_on'
        deduplicated[key] = {
            "from": normalized_from,
            "to": normalized_to,
            "type": rel["type"]
        }

    return list(deduplicated.values())

def extract_relationships(resources):
    """Cria uma lista de relacionamentos com base nas referências nos recursos."""
    relationships = []
    for resource in resources:
        resource_name = resource.get("address")  # Identificador único do recurso
        expressions = resource.get("expressions", {})

        # Verificar referências gerais nas expressões
        for key, value in expressions.items():
            if isinstance(value, dict) and "references" in value:
                for ref in value["references"]:
                    relationships.append({
                        "from": resource_name,
                        "to": ref,
                        "type": "reference"
                    })

        # Adicionar relações explícitas de dependência
        depends_on = resource.get("depends_on", [])
        for dependency in depends_on:
            relationships.append({
                "from": resource_name,
                "to": dependency,
                "type": "depends_on"
            })

    # Remove relacionamentos redundantes e retorna
    return deduplicate_relationships(relationships)

def remove_references_from_resources(resources):
    """
    Remove as referências (expressions.references) dos recursos após extrair os relacionamentos.
    """
    for resource_group in resources.values():
        for resource in resource_group:
            expressions = resource.get("expressions", {})
            for key, value in list(expressions.items()):
                if isinstance(value, dict) and "references" in value:
                    # Remove apenas o campo de referências, preservando outros metadados
                    del expressions[key]["references"]
    return resources

def clean_empty_properties(resources):
    """
    Remove propriedades vazias (objetos ou listas vazias) dos recursos após o processamento.
    """
    for resource_group in resources.values():
        for resource in resource_group:
            # Limpa propriedades vazias diretamente no nível do recurso
            keys_to_remove = [key for key, value in resource.items() if isinstance(value, (dict, list)) and not value]
            for key in keys_to_remove:
                del resource[key]

            # Limpa propriedades vazias dentro de `expressions`, se existir
            if "expressions" in resource:
                keys_to_remove = [key for key, value in resource["expressions"].items() if isinstance(value, (dict, list)) and not value]
                for key in keys_to_remove:
                    del resource["expressions"][key]

                # Remove o campo `expressions` se ele mesmo estiver vazio após a limpeza
                if not resource["expressions"]:
                    del resource["expressions"]

    return resources

def extract_configuration_resources(terraform_json):
    """Extrai e organiza os recursos definidos na configuração do Terraform."""
    resources = terraform_json.get("configuration", {}).get("root_module", {}).get("resources", [])
    if not resources:
        print("No resources found in the Terraform configuration.")
        return {"resources": [], "relationships": []}

    # Mantém os dados completos dos recursos e remove valores nulos e vazios
    cleaned_resources = [remove_empty_values(resource) for resource in resources]
    
    # Organiza os recursos por tipo
    organized_resources = organize_resources_by_type(cleaned_resources)
    
    # Cria os relacionamentos
    relationships = extract_relationships(cleaned_resources)
    
    # Remove referências dos recursos
    organized_resources = remove_references_from_resources(organized_resources)

    # Limpa propriedades vazias dos recursos
    organized_resources = clean_empty_properties(organized_resources)

    return {"resources": organized_resources, "relationships": relationships}

def main():
    # Carregar o JSON do Terraform
    with open("terraform/terraform_state.json", "r") as file:
        terraform_data = json.load(file)

    # Extrair metadados
    metadata = extract_metadata(terraform_data)

    # Extrair recursos e relacionamentos da configuração
    extracted_data = extract_configuration_resources(terraform_data)

    # Combinar metadados, recursos e relacionamentos
    final_data = {
        "metadata": metadata,
        **extracted_data
    }

    # Criar o JSON final
    output_file = "c4_deployment_data.json"
    with open(output_file, "w") as outfile:
        json.dump(final_data, outfile, indent=2)

    print(f"Deployment data saved to '{output_file}'")

if __name__ == "__main__":
    main()