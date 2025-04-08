import sqlite3 as sq


sql_match_type = {
    str: "TEXT",
    int: "INTEGER",
    float: "FLOAT",
    bool: "BOOL",
}


class DatabaseManager:
    def __init__(self, db_path):
        self.con = sq.connect(db_path)
        self.cur = self.con.cursor()
        self.tables = set()  # store table names

    def create_table(self, table_name, entries, force=False):  # [(type, name , entry_type)]
        """Create a table with entries:
        - table_name:str -> the name of the table to create,
        - entries:List(Tuple) -> each entry in a tuple containing (type, name, entry_type)
        where type is either 0(classic key), 1(primary key) or 2(foreign key) ; name must be a string;
        entry_type is either a python_type (str, int, float, etc...) or if entry is a foreign key, entry_type is a tuple
        containing (foreign_db_name:str, foreign_db_key).
        """

        if force:
            instructions_str = "CREATE TABLE "
        else:
            instructions_str = "CREATE TABLE IF NOT EXISTS "
        instructions_str += table_name + "("
        for entry in entries:
            if len(entry) != 3:
                print(
                    "ERROR - Entry is not correctly formatted, refer to documentation."
                )
                continue
            if entry[0] in [0, 1]:  # classic/primary key
                if entry[2] not in sql_match_type:
                    print(
                        "ERROR - the entry type provided is not correct/supported, refer to documentation."
                    )
                    return 2
                primary = "PRIMARY KEY " if entry[0] == 1 else ""

                instructions_str += f"{primary}{entry[1]}{sql_match_type[entry[2]]},"
            elif entry[2] == 0:  # foreign key

                instructions_str += (
                    f"FOREIGN KEY ({entry[1]}) REFERENCES {entry[2][0]}({entry[2][1]})"
                )

        instructions_str += ")"

        self.cur.execute(instructions_str)
        return 0

    def insert_value(self, table_name, to_insert_keys, to_insert_values):
        """Insert a value in an existing table:
        - table_name:str -> the name of the table to insert in,
        - to_insert_keys:tuple(str) -> a tuple containing the name of the keys that will be inserted,
        - to_insert_values:tuple(Any) -> a tuple containing the values to insert MATCHING THE ORDER OF THE GIVEN KEYS.
        """

        if table_name not in self.tables:
            print("ERROR - Cannot add values into a table that does not exist.")
            return 3
        instructions_str = f"INSERT INTO {table_name} ("
        format_str = "("
        if len(to_insert_keys) != len(to_insert_values):
            print(
                "ERROR - The number of values given does not match the number of keys."
            )
            return 4
        for i in range(len(to_insert_keys)):
            if i == len(to_insert_keys) - 1:
                instructions_str += f"{to_insert_values[i]})"
                format_str += r"?)"
            else:
                instructions_str += f"{to_insert_values[i]}, "
                format_str += r"?, "

        self.cur.execute(instructions_str + " VALUES " + format_str, to_insert_values)
        self.con.commit()
        return 0

    def update_value(self, table_name, to_update_keys, to_update_values, condition):
        """Update an entry in an existing table:
        - table_name:str -> the name of the table that will be updated,
        - to_update_keys:tuple(str) -> a tuple containing the name of the keys that will be inserted,
        - to_update_values:tuple(Any) -> a tuple containing the values to insert MATCHING THE ORDER OF THE GIVEN KEYS,
        - condition:str -> a string specifying the condition of the update.
        WARNING : this function executes blindly the condition given, and thus should not be an interface to untrusted-user
        """

        if table_name not in self.tables:
            print("ERROR - Cannot add values into a table that does not exist.")
            return 3
        instructions_str = f"UPDATE {table_name} SET "
        if len(to_update_keys) != len(to_update_values):
            print(
                "ERROR - The number of values given does not match the number of keys."
            )
            return 4
        for i in range(len(to_update_keys)):
            if i == len(to_update_keys) - 1:
                instructions_str += f"{to_update_keys[i]}={to_update_values[i]} "
            else:
                instructions_str += f"{to_update_keys[i]}={to_update_values[i]}, "

        self.cur.execute(instructions_str + "WHERE " + condition)
        self.con.commit()
        return 0

    def query_table(self, instruction):
        """Execute an sql-query:
        - instruction:str -> the query to execute.
        WARNING : this function executes blindly the instruction given, and thus should not be an interface to untrusted-user
        """

        result = self.cur.execute(instruction)
        return result.fetchall()

    def __del__(self):
        self.con.close()
