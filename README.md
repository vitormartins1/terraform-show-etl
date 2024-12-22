1.	Executar o comando terraform show -json: Capturar a saída do estado da infraestrutura gerenciada pelo Terraform em formato JSON.
2.	Processar os dados: Criar um script que extrai apenas as informações úteis para criar diagramas de deployment no estilo C4 Model (e.g., recursos, dependências, relações, tipos).
3.	Gerar um JSON estruturado: Salvar as informações extraídas em um formato limpo e organizado para ser consumido posteriormente por sistemas ou agentes que gerem diagramas.

---

## Processo de ETL para o Terraform

Esta documentação descreve o processo de extração, transformação e carregamento (ETL) dos dados gerados pelo Terraform para estruturar informações de infraestrutura em um formato hierárquico e organizado. O objetivo é transformar os dados brutos em JSON para criar diagramas de deployment no estilo C4 Model.

### 1. Comandos para Gerar o JSON do Terraform State

Para capturar o estado da infraestrutura gerenciada pelo Terraform em formato JSON, execute os seguintes comandos:

```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform show -json tfplan > terraform_state.json
```

**Descrição dos Comandos:**

- `terraform init`: Inicializa o ambiente do Terraform, baixando os provedores necessários.
- `terraform plan -out=tfplan`: Gera um plano (tfplan) para aplicar as mudanças descritas no código Terraform.
- `terraform show -json tfplan > terraform_state.json`: Converte o plano gerado (tfplan) em um arquivo JSON detalhado, chamado `terraform_state.json`.

O arquivo `terraform_state.json` é a entrada principal para o processo de ETL. Ele contém todas as informações sobre os recursos configurados e planejados pelo Terraform.

### 2. Estrutura do JSON Gerado

O arquivo JSON gerado possui as seguintes seções principais:

	1.	configuration:
	•	Representa a configuração declarada no código Terraform.
	•	Inclui:
		•	root_module.resources: Reflete os recursos declarados no código, incluindo expressões, referências e metadados detalhados.
	2.	planned_values:
	•	Representa o estado final planejado dos recursos.
	•	Contém informações resolvidas, como IDs, ARNs, e outros metadados calculados.
	3.	resource_changes:
	•	Lista as mudanças que o Terraform irá realizar.
	•	Exibe o estado antes (before) e depois (after) das alterações.
	•	Contém apenas os recursos que sofrerão mudanças, e não o estado completo.
	4.	output_changes:
	•	Detalha as mudanças nos outputs definidos no código Terraform.

3. Estruturação do JSON Extraído

Após o processamento, o JSON é transformado em um formato hierárquico, organizado em:
	•	Provedor: Agrupa todos os recursos de um único provedor (exemplo: aws).
	•	Região: Agrupa os recursos por região configurada (exemplo: us-east-1).
	•	Hierarquia de Recursos:
	•	Recursos são organizados conforme dependências ou associações.
	•	Exemplo de estrutura:

{
  "aws": {
    "us-east-1": {
      "vpcs": [
        {
          "vpc_id": "aws_vpc.main",
          "subnets": [
            {
              "subnet_id": "aws_subnet.example",
              "security_groups": [
                {
                  "group_id": "aws_security_group.example",
                  "instances": [...]
                }
              ]
            }
          ]
        }
      ],
      "s3_buckets": [...],
      "sns_topics": [...],
      "other_resources": [...]
    }
  }
}

4. Relacionamentos

Os relacionamentos extraídos são organizados separadamente, com base nas dependências e associações entre os recursos. Cada relacionamento segue o seguinte formato:

```json
{
  "from": "aws_sns_topic_subscription.example_subscription",
  "to": "aws_sqs_queue.example_queue",
  "type": "reference"
}
```

•	Campos Importantes:
	•	from: Identificador do recurso de origem.
	•	to: Identificador do recurso de destino.
	•	type: Define o tipo do relacionamento (reference ou depends_on).

5. Processamento e Limpeza

Durante o processo ETL, as seguintes etapas são realizadas:
	1.	Remoção de Campos Desnecessários:
	•	Campos como type (já agrupados por tipo) e provider_config_key são removidos.
	2.	Eliminação de Propriedades Vazias:
	•	Objetos e listas vazias são excluídos após o processamento.
	3.	Organização Hierárquica:
	•	Recursos são estruturados hierarquicamente, com base em VPCs, regiões, e outros agrupamentos naturais.

6. Uso do JSON Final

O JSON final é preparado para:
	•	Ser consumido por sistemas ou agentes de IA que geram diagramas no formato C4 Model.
	•	Facilitar visualizações hierárquicas e análises de infraestrutura.

Se precisar de ajustes ou novas funcionalidades, esta estrutura pode ser facilmente expandida para incluir outros provedores ou comportamentos específicos.