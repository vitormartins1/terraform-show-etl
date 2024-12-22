1.	Executar o comando terraform show -json: Capturar a saída do estado da infraestrutura gerenciada pelo Terraform em formato JSON.
2.	Processar os dados: Criar um script que extrai apenas as informações úteis para criar diagramas de deployment no estilo C4 Model (e.g., recursos, dependências, relações, tipos).
3.	Gerar um JSON estruturado: Salvar as informações extraídas em um formato limpo e organizado para ser consumido posteriormente por sistemas ou agentes que gerem diagramas.

---

## Processo de ETL para o Terraform

Esta seção documenta os comandos e regras utilizadas no processo de ETL para a análise do JSON gerado pelo Terraform. Ela também detalha as partes importantes do arquivo JSON e como os dados são extraídos e estruturados.

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
•	Inclui a subestrutura:
•	root_module.resources: Reflete os recursos exatamente como descritos no código, incluindo expressões, referências e outras informações detalhadas.
2.	planned_values:
•	Representa o estado final planejado dos recursos.
•	Contém informações completas e resolvidas, como IDs, ARNs, e outros metadados calculados.
3.	resource_changes:
•	Lista as mudanças que o Terraform irá realizar.
•	Mostra o estado antes (before) e depois (after) das alterações.
•	Contém apenas os recursos que sofrerão mudanças, e não o estado completo.
4.	output_changes:
•	Detalha as mudanças em outputs definidos no código Terraform.
