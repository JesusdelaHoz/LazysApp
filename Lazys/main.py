import db
from models import *

if __name__ == '__main__':
    db.Base.metadata.create_all(db.engine)
    root = Tk()
    app = FicheroLazLas(root)
    root.mainloop()