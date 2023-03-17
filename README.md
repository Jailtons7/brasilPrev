# BrasPrev

Uma API Rest que possibilita cadastro de clientes e produtos, 
contratações de planos, aportes financeiros extras e resgates

Esta API foi construída em Python com Django/DRF, com banco de dados 
PostgresQL, está dockerizada, tem documentação e contém testes de 
unidade e de integração.

### Arquitetura das pastas

`/api/` - Pasta principal da aplicação, é nela onde estão os models, views, serializers, rotas e 
todas as regras de negócios da aplicação.

`/etc/` - Pasta com os arquivos de configuração do nginx para deixar a 
aplicação pronta para odeploy.

`/brasilPrev/` - Pasta com o arquivo de configurações e as urls principais da aplicação

`/staticfiles/` - Pasta com arquivos estáticos do Django Admin e DRF

### Rodando a aplicação
Para facilitar os comandos eu usei o `make` num ambiente ubuntu,
mas se não o tiver instalado, basta executar cada um dos comandos 
correspondentes no arquivo `Makefile`.

Para criar a imagem da aplicação, na raiz do projeto basta executar 
`make build`

Em seguida será possível rodar a aplicação com o servidor local do django
```shell
make runserver  # útil para debug
# equivale a: docker-compose run --rm --service-port web python manage.py runserver 0.0.0.0:8002 --insecure
```
ou com o nginx
```shell
make up  # fundamental para o deploy
```

Após colocar a api no ar basta acessar `/api/docs/` para acessar a documentação.

> Dica importante: configurei de forma que a porta seja `8002` localmente e `1337` no nginx, portanto se rodar a 
aplicação com `make runserver` o domínio será `0.0.0.0:8002`, se rodar com `make up` será `127.0.0.1:1337` 

Além dos comandos acima também é possível rodar todos os comandos mais comuns 
para desenvolvimento com django:

```shell
make createsuperuser
```
```shell
make makemigrations
```
```shell
make migrate
```
```shell
make collectstatic
```

### Rodando testes

```shell
make tests
```
