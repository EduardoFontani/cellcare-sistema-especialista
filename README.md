# 📱 CellCare — Sistema Especialista para Diagnóstico de Celulares

## 📌 Sobre o projeto

O **CellCare** é um sistema especialista desenvolvido em Python para a empresa fictícia **CellCare Assistência Técnica**, especializada em manutenção e conserto de celulares.

O sistema tem como objetivo auxiliar na identificação de possíveis defeitos em aparelhos celulares, utilizando respostas fornecidas pelo usuário e uma base de conhecimento composta por fatos e regras.

A partir das informações coletadas, o sistema realiza inferências, apresenta possíveis diagnósticos e sugere procedimentos de manutenção, incluindo estimativas de custo, prazo e urgência.

## 🎯 Objetivos

- Identificar possíveis problemas em aparelhos celulares.
- Automatizar uma avaliação inicial de defeitos.
- Aplicar regras de conhecimento para chegar a conclusões.
- Apresentar recomendações de manutenção.
- Explicar como e por que determinada conclusão foi alcançada.
- Demonstrar na prática o funcionamento de um sistema especialista.

## ⚙️ Funcionalidades

- Questionário interativo para coleta de informações sobre o aparelho.
- Base de conhecimento externa em formato JSON.
- 32 regras de produção no formato SE–ENTÃO.
- Motor de inferência com encadeamento para frente (*Forward Chaining*).
- Utilização de fatores de certeza para representar o grau de confiança das conclusões.
- Identificação de possíveis defeitos em tela, bateria, conector, placa, câmera, áudio e conectividade.
- Recomendações de manutenção.
- Estimativas de custos e prazos de serviço.
- Mecanismo de explicação com as opções "Por quê?" e "Como?".
- Validação de respostas e tratamento de entradas inválidas.

## 🧠 Como funciona o sistema

O CellCare utiliza a arquitetura tradicional de um sistema especialista, organizada em três partes principais:

### 1. Base de conhecimento

Armazena os fatos, perguntas, regras e possíveis diagnósticos em um arquivo JSON.

As regras seguem a estrutura:

**SE** determinadas condições forem verdadeiras, **ENTÃO** uma conclusão poderá ser gerada.

Exemplo:

- SE o aparelho não carrega e o cabo fica folgado na entrada;
- ENTÃO o sistema identifica uma possível falha no conector de carga.

### 2. Motor de inferência

Implementado em Python, o motor utiliza o método de encadeamento para frente (*Forward Chaining*).

O funcionamento ocorre da seguinte maneira:

1. O usuário responde às perguntas.
2. As respostas são armazenadas como fatos.
3. O motor verifica quais regras possuem condições satisfeitas.
4. As regras aplicáveis geram novas conclusões.
5. As conclusões podem ativar outras regras.
6. O processo continua até que não existam novas conclusões.

### 3. Mecanismo de explicação

O sistema possui dois mecanismos de explicação:

- **Por quê?** — informa por que determinada pergunta é importante para o diagnóstico.
- **Como?** — apresenta os fatos e as regras utilizados para chegar à conclusão.

## 📊 Fatores de certeza

O projeto utiliza fatores de certeza (*Certainty Factors*) para representar o grau de confiança das conclusões.

Os valores são representados em uma escala de 0 a 1, equivalente a 0% até 100%.

Cada regra possui um fator de certeza próprio, e as evidências podem ser combinadas quando diferentes regras apontam para a mesma conclusão.

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento do sistema |
| JSON | Armazenamento da base de conhecimento |
| Forward Chaining | Método de inferência |
| Certainty Factors | Representação de certeza |
| Git e GitHub | Versionamento e hospedagem do projeto |

## 📁 Estrutura do projeto

```text
cellcare-sistema-especialista/
│
├── base_conhecimento.json  # Perguntas, fatos, regras e diagnósticos
├── main.py                 # Arquivo principal e interação com o usuário
├── motor.py                # Motor de inferência
├── test_motor.py           # Testes do motor de inferência
├── README.md               # Documentação do projeto
└── .gitignore              # Arquivos ignorados pelo Git
```

## 💻 Requisitos para execução

- Python 3 instalado.
- Git (opcional, para clonar o repositório).
- Terminal, Prompt de Comando ou VS Code.

O projeto utiliza recursos da biblioteca padrão do Python, não exigindo instalação de bibliotecas externas para a versão de terminal.

## 🚀 Como instalar e executar

### 1. Clonar o repositório

```bash
git clone https://github.com/EduardoFontani/cellcare-sistema-especialista.git
```

### 2. Entrar na pasta do projeto

```bash
cd cellcare-sistema-especialista
```

### 3. Executar o sistema

```bash
python main.py
```

Caso o comando `python` não funcione no Windows, tente:

```bash
py main.py
```

## 🧪 Testes

O projeto possui um arquivo de testes chamado `test_motor.py`, destinado à verificação do funcionamento do motor de inferência.

Para executar os testes, utilize o comando:

```bash
python -m unittest
```

## ⚠️ Limitações

O CellCare é um protótipo acadêmico desenvolvido para demonstrar conceitos de Inteligência Artificial e Sistemas Especialistas.

Os diagnósticos são sugestões baseadas nas informações fornecidas e nas regras cadastradas. Eles não substituem a avaliação técnica presencial de um profissional especializado.

## 🎓 Finalidade acadêmica

Projeto desenvolvido para a disciplina **Programação de Sistemas Especialistas**, da Universidade Veiga de Almeida (UVA).

**Repositório:**  
https://github.com/EduardoFontani/cellcare-sistema-especialista

## 👨‍💻 Integrantes

- EDUARDO FONTANI 
- LUCAS TRINDADE
- TIAGO OLIVEIRA
