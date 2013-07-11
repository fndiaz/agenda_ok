agenda = db.define_table("agenda",
      Field("empresa", notnull=True),
      Field("telefone", notnull=True, unique=True),
      Field("contato"),
      Field("dep"),
      Field("particular", "boolean"),
      Field("ramal", writable=False),
      #auth.signature
      format="%(nome)s")

agenda_lg = db.define_table("agenda_lg",
      Field("ramal"),
      Field("telefone"),
      Field("empresa"),
      Field("datetime"),
      Field('particular'),
      #auth.signature
      format="%(nome)s")





