## Database Management (`database.py`)

*requirements* : `sqlite3`

This module implement a class `DatabaseManager` that controls one database file.
Each database file can contains multiple tables. Using SQLite, only single-file
references are possible.

### References

`DatabaseManager(self, db_path)` : initiates the connection (and db-cursor) with the database at the given path. Creates it if the given path does not exist.

`DatabaseManager.create_table(self, table_name, entries)` : creates a table with the name `table_name` with the columns specified by the **list of tuple(s)** `entries`.
 - table_name:str -> the name of the table to create,
 - entries:List(Tuple) -> a list of entries in tuples containing (type, name, entry_type);
    Each entry must be formatted as followed :
     - An entry type (`int`) : `0` for *classic key*, `1` for *primary key* and *2* for *foreign/reference key*;
     - An entry name (`str`): the name of the columns/entry;
     - The entry information(`type|str|tuple`) :
        - a supported datatype (see [supported datatype entry](#supported-data-type-entry))
        - a tuple `(reference_table_name, reference_table_entry)` specifying the reference information.

`DatabaseManager.insert_value(self, table_name, to_insert_keys, to_insert_values)` : inserts a value in an existing table.
 - table_name:`str` -> the name of the table to insert in
 - to_insert_keys:`tuple(str)` -> a tuple containing the name of the keys that will be inserted,
 - to_insert_values:`tuple(Any)` -> a tuple containing the values to insert MATCHING THE ORDER OF THE GIVEN KEYS.


`DatabaseManager.query_table(self, instruction)` : executes an sql-query:
 - instruction:`str` -> the query to execute.
> [!WARNING]
> this function executes blindly the instruction given, and thus should not be an interface to untrusted-user

### Miscellaneous

#### Supported datatype entry
- `"TEXT", "text", str` : match the "TEXT" datatype of SQLite
- `"INT","INTEGER", "int", "integer", int` : match the "INTEGER" datatype of SQLite
- `"FLOAT", "float", float` : match the "FLOAT" datatype of SQLite
- `"BOOL", "bool", bool` : match the "BOOL/BOOLEAN" datatype of SQLite
- `"DATE", "date"` : match the "DATE" datatype of SQLite.
- `"NULL", None`: match the "NULL" datatype of SQLite.



