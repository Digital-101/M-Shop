To create a **manager role** in your database using only SQL queries, you can follow the steps below. This assumes that you have a `roles` table and a `users` table (or equivalent) with a relationship between them.

### 1. **Create a `roles` table (if it doesn't exist)**
First, if you don't have a `roles` table, you'll need to create one. This table will store role types (like `admin`, `manager`, `user`).

Here's an SQL query to create the `roles` table:

```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);
```

### 2. **Insert the 'manager' role into the `roles` table**
Once the `roles` table is created, insert the `manager` role:

```sql
INSERT INTO roles (name)
VALUES ('manager');
```

### 3. **Update the `users` table (if necessary)**
To assign roles to users, you'll need a relationship between the `users` table and the `roles` table. You can achieve this with a foreign key column in the `users` table. If your `users` table doesn't already have a `role_id`, you need to add it:

```sql
ALTER TABLE users
ADD COLUMN role_id INTEGER REFERENCES roles(id);
```

This creates a foreign key relationship between `users.role_id` and `roles.id`.

### 4. **Assign the 'manager' role to a user**
Now, you can assign the `manager` role to a specific user by updating the `role_id` field in the `users` table. First, find the `id` of the `manager` role:

```sql
SELECT id FROM roles WHERE name = 'manager';
```

Assuming that returns the role ID (let's say it's `2`), assign it to a user. For example, if the user has an `id` of `1`, you can update that user’s role:

```sql
UPDATE users
SET role_id = 2
WHERE id = 1;
```

Now, the user with `id = 1` will have the `manager` role.

### 5. **(Optional) Check the Results**
You can verify the `roles` and `users` tables using these queries:

- List all roles:
    ```sql
    SELECT * FROM roles;
    ```

- List all users and their roles (assuming a join is possible):
    ```sql
    SELECT users.username, roles.name as role
    FROM users
    LEFT JOIN roles ON users.role_id = roles.id;
    ```

This SQL-based approach will create a `manager` role and assign it to a user in your database.