workspace {
    model {
        live = deploymentEnvironment "Live" {
            deploymentNode "Amazon Web Services" {
                tags "Amazon Web Services - Cloud"

                deploymentNode "Enterprise" {
                    tags "Amazon Web Services - Server contents"

                    deploymentNode "us-east-1" {
                        tags "Amazon Web Services - Region"

                        # Grupo Managed
                        deploymentNode "Managed" "terraform" "repo-infra-sns-com-sqs" {
                            tags "Terraform Managed Resources" 

                            deploymentNode "Amazon SNS" {
                                tags "Amazon Web Services - Simple Notification Service SNS"
                                snsTopic = infrastructureNode "SNS Topic" {
                                    description "Tópico SNS usado para distribuir mensagens."
                                    technology "SNS Topic"
                                    tags "Amazon Web Services - Simple Notification Service SNS Topic"
                                }
                                snsSubscription = infrastructureNode "SNS Subscription" {
                                    description "Assinatura SNS para enviar mensagens para a fila."
                                    technology "SNS Subscription"
                                    tags "Amazon Web Services - Simple Notification Service SNS HTTP Notification"
                                    snsTopic -> snsSubscription "Distributes messages"
                                }
                            }

                            deploymentNode "Amazon SQS" {
                                tags "Amazon Web Services - Simple Queue Service SQS"
                                sqsQueue = infrastructureNode "SQS Queue" {
                                    description "Fila que recebe mensagens do tópico SNS."
                                    technology "AWS SQS"
                                    tags "Amazon Web Services - Simple Queue Service SQS Queue"
                                }

                                snsSubscription -> sqsQueue "Deliver messages to SQS"
                            }

                            deploymentNode "Amazon IAM" {
                                tags "Amazon Web Services - Identity and Access Management IAM"
                                
                                sqsQueuePolicy = infrastructureNode "SQS Queue Policy" {
                                    description "Política associada à fila SQS."
                                    technology "AWS SQS Policy"
                                    tags "Amazon Web Services - Identity and Access Management IAM Permissions"
                                }

                                sqsQueuePolicy -> sqsQueue "Apply Policy to Queue"
                            }

                            snsSubscription -> sqsQueuePolicy "Depends On"
                        }

                        tags "Terraform Data Resources"

                        deploymentNode "Amazon SSM" {
                            tags "Amazon Web Services - Systems Manager"
                            parameter = infrastructureNode "SSM Parameter Store" {
                                description "Parâmetro usado para configuração."
                                technology "AWS SSM Parameter"
                                tags "Amazon Web Services - Systems Manager Parameter Store"
                            }
                        }

                        snsTopic -> parameter "Reference SSM Parameter"
                    }
                }
            }
        }
    }
    views {
        styles {
            relationship "Depends On" {
                color #0000FF
                thickness 2
                style solid
                fontSize 24
                position 90
                routing direct
            }
            
            element "Element" {
                background #ffffff
            }
            
            element "Terraform Managed Resources" {
                color #000000
                stroke #000000
                icon "https://git-scm.com/images/logos/downloads/Git-Icon-Black.png"
            }
        }

        deployment * live "deploy" {
            include *
            autoLayout lr
        }

        theme https://static.structurizr.com/themes/amazon-web-services-2020.04.30/theme.json
    }
}