-- create and populate size table
use seade

DROP TABLE IF EXISTS size;
CREATE TABLE size(
    size INTEGER,
    relation VARCHAR(255)
);

INSERT INTO size SELECT COUNT(*), "casos" FROM casos;


-- create history table
DROP TABLE IF EXISTS history;
CREATE TABLE history(
    content VARCHAR(1000)
);

-- add fulltext index for publication (only run once)
ALTER TABLE casos ADD FULLTEXT(nome_munic);
ALTER TABLE casos ADD FULLTEXT(regiao);
ALTER TABLE casos ADD FULLTEXT(obito);
ALTER TABLE casos ADD FULLTEXT(raca_cor);
-- ALTER TABLE casos ADD FULLTEXT(idade);
ALTER TABLE casos ADD FULLTEXT(cs_sexo);
ALTER TABLE casos ADD FULLTEXT(diagnostico_covid19);
ALTER TABLE casos ADD FULLTEXT(asma);
ALTER TABLE casos ADD FULLTEXT(cardiopatia);
ALTER TABLE casos ADD FULLTEXT(diabetes);
ALTER TABLE casos ADD FULLTEXT(doenca_hematologica);
ALTER TABLE casos ADD FULLTEXT(doenca_hepatica);
ALTER TABLE casos ADD FULLTEXT(doenca_neurologica);
ALTER TABLE casos ADD FULLTEXT(doenca_renal);
ALTER TABLE casos ADD FULLTEXT(imunodepressao);
ALTER TABLE casos ADD FULLTEXT(obesidade);
ALTER TABLE casos ADD FULLTEXT(pneumopatia);
ALTER TABLE casos ADD FULLTEXT(puerpera);
ALTER TABLE casos ADD FULLTEXT(sindrome_de_down);
