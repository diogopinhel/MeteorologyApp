# Aplicação de Meteorologia

Esta aplicação de Meteorologia fornece informações meteorológicas em tempo real e previsões, incluindo alertas críticos de condições climáticas. Os utilizadores podem pesquisar dados meteorológicos pelo nome da cidade ou por coordenadas geográficas. A aplicação também oferece uma visualização de dados históricos e envia notificações por e-mail para previsões semanais e alertas críticos.

## Recursos

- **Informações Meteorológicas em Tempo Real**: Pesquisar dados meteorológicos atuais pelo nome da cidade ou coordenadas.
- **Previsão do Tempo**: Obter uma previsão do tempo de 5 dias com resumos detalhados diários.
- **Dados Históricos**: Visualizar dados históricos meteorológicos salvos num banco de dados SQLite local.
- **Notificações por E-mail**: Receber previsões semanais e alertas críticos por e-mail.
- **Alertas Críticos**: Enviar automaticamente notificações por e-mail para condições climáticas críticas como furacões, tornados e inundações.

## Instalação

### Pré-requisitos

- Python 3.8 ou superior (se estiver a rodar a partir do código fonte)

### Configuração

Uma vez que o utilizador está rodar a aplicação a partir do código fonte, siga os passos abaixo:

1. **Instalar Bibliotecas através do CMD**:
   
   Passo 1: Pressione as teclas "Win + R" ao mesmo tempo no teclado.

   Passo 2: Na caixa de diálogo "Executar" que aparece, digite "cmd".

   Passo 3: Pressione Enter ou clique no botão "OK".
   
Depois de abrir o CMD, irá visualizar uma janela preta com texto branco, onde pode digitar comandos.

   Passo 4: Escreva o seguinte comando no CMD para instalar as bibliotecas necessárias à aplicação:

   ```bash
   pip install Pillow==8.4.0 ttkbootstrap==0.5.1 requests==2.26.0 matplotlib==3.4.3 
```

### Interface Principal

- **PEsquisar Clima**: Insira o nome de uma cidade ou coordenadas (latitude e longitude) e clique em "Pesquisar" para pesquisar dados meteorológicos.
- **Ver Previsão**: A aplicação exibe uma previsão de 5 dias com resumos diários.
- **Dados Históricos**: Clique em "Ver Histórico" para visualizar dados meteorológicos passados.
- **Alertas Meteorológicos**: Alertas críticos de condições meteorológicas são exibidos, e os utilizadores serão notificados por e-mail se estiverem habilitados.
- **Notificações por E-mail**: Marque "Receber previsões por email" e forneça seu endereço de e-mail para receber previsões semanais e alertas.

**Notificações por E-mail**

- A aplicação envia previsões semanais e alertas críticos de condições meteorológicas para o endereço de e-mail especificado.
- Alertas críticos incluem condições favoráveis para furacões, tornados, inundaçõese tempestades severas.
