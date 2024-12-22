# terraform-show-etl

## Processo de ETL para o Terraform

Esta documentação descreve o processo de extração, transformação e organização dos dados gerados pelo Terraform, com o objetivo de criar um JSON estruturado para gerar diagramas de deployment de infraestrutura (C4 Deployment).

## Visão Geral

Este script processa os dados gerados pelo comando `terraform show -json`, extraindo informações sobre recursos, metadados e relacionamentos definidos no Terraform. O resultado é um JSON consolidado que organiza recursos por tipo e extrai relacionamentos explícitos e referências implícitas.

## Comandos para Gerar o JSON

Antes de executar o script Python, você precisa gerar o JSON de entrada a partir do Terraform:

1.	Inicialize o Terraform:

```bash
terraform init
```

2.	Planeje as mudanças:

```bash
terraform plan -out=tfplan
```

3.	Gere o JSON:

```bash
terraform show -json tfplan > terraform_state.json
```

O arquivo `terraform_state.json` é a entrada principal para o script Python.

## Estrutura do Script

O script é dividido em etapas principais:

**1. Remoção de Valores Vazios**

A função `remove_empty_values` elimina valores nulos, listas vazias e objetos vazios do JSON para simplificar os dados:

```python
def remove_empty_values(obj):
    # Remove valores nulos, listas e objetos vazios
```

**2. Extração de Metadados**

A função `extract_metadata` extrai informações sobre o provedor (e.g., AWS) e a região:

```python
def extract_metadata(terraform_json):
    # Extrai o provedor e a região do JSON
```

**3. Organização de Recursos por Tipo**

A função `organize_resources_by_type` agrupa os recursos extraídos por tipo (e.g., `aws_instance`, `aws_security_group`):

```python
def organize_resources_by_type(resources):
    # Agrupa os recursos por tipo
```

**4. Extração de Relacionamentos**

A função `extract_relationships` analisa explicitamente os campos `depends_on` e referências em expressions para identificar dependências explícitas:

```python
def extract_relationships(resources):
    # Extrai relacionamentos explícitos entre os recursos
```

**Tipos de Relacionamentos:**

- `depends_on`: Dependências explícitas declaradas no código Terraform.
- `reference`: Referências diretas a outros recursos encontradas em expressions.

**5. Limpeza de Dados**

As funções `remove_references_from_resources` e `clean_empty_properties` eliminam campos desnecessários e propriedades vazias para deixar o JSON final mais legível e útil:

```python
def remove_references_from_resources(resources):
    # Remove referências após extraí-las
```

```python
def clean_empty_properties(resources):
    # Remove propriedades vazias do JSON final
```

## Fluxo do Script

O fluxo principal do script está encapsulado na função `extract_configuration_resources`:

```python
def extract_configuration_resources(terraform_json):
    # Extrai e organiza os recursos, relacionamentos e limpa os dados
```

**Etapas:**

1. Carregar os dados do Terraform (`terraform_state.json)`.
2. Organizar os recursos por tipo.
3. Extrair relacionamentos explícitos.
4. Limpar valores desnecessários e referências extraídas.

## Saída Final

O script gera um arquivo chamado `c4_deployment_data.json` contendo:

1.	Metadados:
	- Provedor (`provider`) e região (`region`).

2.	Recursos:
	- Estruturados por tipo (e.g., `aws_instance`, `aws_security_group`).

3.	Relacionamentos:
	- Relacionamentos explícitos entre os recursos.

**Formato Exemplo:**

```json
{
  "metadata": {
    "provider": "aws",
    "region": "us-east-1"
  },
  "resources": {
    "aws_instance": [
      {
        "address": "aws_instance.example_instance",
        "type": "aws_instance",
        "expressions": {
          "ami": {
            "constant_value": "ami-12345678"
          },
          "instance_type": {
            "constant_value": "t2.micro"
          }
        }
      }
    ],
    "aws_security_group": [
      {
        "address": "aws_security_group.example_sg",
        "type": "aws_security_group",
        "expressions": {
          "name": {
            "constant_value": "example-security-group"
          }
        }
      }
    ]
  },
  "relationships": [
    {
      "from": "aws_instance.example_instance",
      "to": "aws_security_group.example_sg",
      "type": "reference"
    }
  ]
}
```

## Conclusão

O script transforma os dados brutos do Terraform em um JSON estruturado para facilitar a criação de diagramas de deployment ou outras análises de infraestrutura.
