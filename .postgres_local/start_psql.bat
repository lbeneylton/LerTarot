
REM Iniciar banco automaticamente
pgsql/bin/initdb -D ./postgres/data  -U postgres -A password --pwfile=senha.txt

REM Iniciar servidor
pgsql/bin/pg_ctl -D ./postgres/data start

REM Salvar senha em variavel de ambiente para operações futuras
REM set PGPASSWORD=minhasenha

REM Criar banco
pgsql/bin/createdb -U postgres lertarot

REM Executar script inicial
pgsql/bin/psql -U postgres -d lertarot -f init.sql

REM Desliga servidor
pgsql/bin/pg_ctl -D ./postgres/data stop -m smart


@REM Host=localhost
@REM Port=5432
@REM Database=meusistema
@REM Username=app
@REM Password=123