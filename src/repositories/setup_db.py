from src.repositories import PostgresBankRepository


def main() -> None:
    PostgresBankRepository().initialize_schema()
    print("PostgreSQL schema is ready.")


if __name__ == "__main__":
    main()
