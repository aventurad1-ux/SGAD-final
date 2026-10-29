from app import create_app
from app.extensions import db
from app.models.categoria_repositorio import CategoriaRepositorio


CATEGORIAS_INICIALES = [
    "Documentos de Dirección",
    "Actas y reuniones",
    "Administración",
    "Documentos académicos",
    "Evidencias docentes",
    "Correspondencia",
    "Otros",
]


def seed_repositorio():
    app = create_app()

    with app.app_context():
        creadas = 0
        existentes = 0

        for nombre in CATEGORIAS_INICIALES:
            categoria = CategoriaRepositorio.query.filter(
                db.func.lower(CategoriaRepositorio.nombre)
                == nombre.lower()
            ).first()

            if categoria:
                existentes += 1
                print(
                    f"[EXISTE] {categoria.nombre}"
                )
                continue

            nueva_categoria = CategoriaRepositorio(
                nombre=nombre,
                activa=True
            )

            db.session.add(
                nueva_categoria
            )

            creadas += 1

            print(
                f"[CREADA] {nombre}"
            )

        db.session.commit()

        print("")
        print(
            "Seed de Repositorio institucional completado."
        )
        print(
            f"Categorías creadas: {creadas}"
        )
        print(
            f"Categorías existentes: {existentes}"
        )


if __name__ == "__main__":
    seed_repositorio()