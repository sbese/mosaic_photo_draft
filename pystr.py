from psycopg2 import connect

con = connect(database="mosaic_raibow", user="postgres", password="zaq!23", host="127.0.0.1")
cur = con.cursor()

# s = 'create table pic_rainbow (url text not null unique, r   integer not null, g   integer not null, b   integer not null'+ ' '.join([f"color_{r}_{g}_{b} integer not null," for r in range(8) for g in range(8) for b in range(8)])[0:-1]+')'

ss = [f"""create table color_{r}_{g}_{b}
(
    pic_id   integer not null
        constraint col_0_0_0_mosaic_pic_id_fk
            references mosaic_pic
            on delete cascade,
    distance integer not null
);"""  for r in range(8) for g in range(8) for b in range(8)]

for s in ss:
    cur.execute(s)
    con.commit()
    print(s)

# text not null unique