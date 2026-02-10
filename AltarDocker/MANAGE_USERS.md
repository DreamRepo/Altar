# User Management — MongoDB and MinIO

This guide covers creating users and managing access for MongoDB and MinIO in your Altar stack.

---

## 1. MongoDB

### Connecting to the MongoDB shell (mongosh)

To manage users, you need to connect to the MongoDB shell inside the container.

#### Connect as admin (recommended)

```bash
docker exec -it mongo_altar mongosh -u admin -p changeme123 --authenticationDatabase admin
```

> **Note:** Replace `admin` and `changeme123` with your actual credentials if you've customized `MONGO_ROOT_USER` and `MONGO_ROOT_PASSWORD` in your `.env` file.

#### Connect as a specific user

```bash
# User created in admin database
docker exec -it mongo_altar mongosh -u username -p password123 --authenticationDatabase admin

# User created in a specific database (e.g., sacred)
docker exec -it mongo_altar mongosh -u username -p password123 --authenticationDatabase sacred
```

#### Connect from outside Docker (host machine)

If you have `mongosh` installed locally:

```bash
# As admin
mongosh "mongodb://admin:changeme123@localhost:27017/admin"

# To a specific database
mongosh "mongodb://admin:changeme123@localhost:27017/sacred?authSource=admin"
```

---

### Understanding authentication databases

When creating a MongoDB user, you choose **where** to create them: in the `admin` database or in a specific database (e.g., `sacred`). This choice affects how users authenticate.

| Created in | Auth source | Best for |
|------------|-------------|----------|
| `admin` | `--authenticationDatabase admin` | Admins, users needing access to multiple databases |
| Specific DB (e.g., `sacred`) | `--authenticationDatabase sacred` | Users working only with that database |

#### Users in the `admin` database

- Can be granted roles on **any database**
- Authenticate with `--authenticationDatabase admin`
- Ideal for: administrators, service accounts, users accessing multiple databases

```javascript
use admin
db.createUser({
  user: "multi_db_user",
  pwd:  "password123",
  roles: [
    { role: "readWrite", db: "sacred" },
    { role: "read", db: "other_db" }
  ]
})
```

Connection string:
```
mongodb://multi_db_user:password123@localhost:27017/sacred?authSource=admin
```

#### Users in a specific database

- Can only have roles on **that database**
- Authenticate with `--authenticationDatabase <database_name>`
- Ideal for: single-purpose users, simpler access control, isolating permissions

```javascript
use sacred
db.createUser({
  user: "sacred_user",
  pwd:  "password123",
  roles: [ { role: "readWrite", db: "sacred" } ]
})
```

Connection string:
```
mongodb://sacred_user:password123@localhost:27017/sacred?authSource=sacred
```

#### Which should I use?

| Scenario | Recommendation |
|----------|----------------|
| User only needs access to `sacred` | Create in `sacred` database |
| User needs access to multiple databases | Create in `admin` database |
| Administrative user (backup, monitoring) | Create in `admin` database |
| Application service account | Either works; `admin` is more flexible |

> **Tip:** When in doubt, create users in the `admin` database — it's more flexible and you can always limit their roles to specific databases.

---

### Create a new user

Connect to MongoDB:
```bash
docker exec -it mongo_altar mongosh
```

#### Option A: Create user in `admin` database (recommended)

```javascript
use admin
db.createUser({
  user: "username",
  pwd:  "password123",
  roles: [ { role: "readWrite", db: "sacred" } ]
})
```

#### Option B: Create user in specific database

```javascript
use sacred
db.createUser({
  user: "username",
  pwd:  "password123",
  roles: [ { role: "readWrite", db: "sacred" } ]
})
```

### Available roles

| Role        | Description                          |
|-------------|--------------------------------------|
| `read`      | Read-only access to the database     |
| `readWrite` | Read and write access to the database|

### Example: Read-only user

```javascript
use admin
db.createUser({
  user: "readonly_user",
  pwd:  "password123",
  roles: [ { role: "read", db: "sacred" } ]
})
```

Connection string for this user:
```
mongodb://readonly_user:password123@localhost:27017/sacred?authSource=admin
```

---

### Manage existing users

Connect to the database where the user was created:

```bash
docker exec -it mongo_altar mongosh
```

#### List all users

```javascript
// Users in admin database
use admin
db.getUsers()

// Users in sacred database
use sacred
db.getUsers()
```

#### View a specific user's roles

```javascript
use admin
db.getUser("username")
```

#### Grant additional roles

Add new roles to an existing user:

```javascript
use admin
db.grantRolesToUser("username", [
  { role: "readWrite", db: "another_db" }
])
```

#### Revoke roles

Remove roles from a user:

```javascript
use admin
db.revokeRolesFromUser("username", [
  { role: "readWrite", db: "sacred" }
])
```

#### Change user password

```javascript
use admin
db.changeUserPassword("username", "new_password123")
```

#### Delete a user

```javascript
use admin
db.dropUser("username")
```

> **Note:** Always use the database where the user was created (`use admin` or `use sacred`).

---

## 2. MinIO

The easiest way to manage MinIO users is through the web console.

### Access the console

1. Open http://localhost:9001 (or your configured console port)
2. Log in with your MinIO admin credentials (`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`)

### Create a policy

1. Go to **Administrator** → **Policies**
2. Click **Create Policy +** in the top right
3. Enter a policy name and paste the JSON

#### Read/Write policy example

Allows read and write access to specific buckets:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowBucketReadWrite",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:HeadBucket",
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:PutObject",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::bucket-name",
                "arn:aws:s3:::bucket-name/*"
            ]
        }
    ]
}
```

> **Note:** Users can read/write to existing buckets but cannot create new ones. Create buckets as admin: **Administrator** → **Buckets** → **Create Bucket**.

> **Important:** Bucket names can only contain lowercase letters (`a-z`), numbers (`0-9`), and hyphens (`-`).

#### Read-only policy example

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowReadOnly",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:HeadBucket",
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::bucket-name",
                "arn:aws:s3:::bucket-name/*"
            ]
        }
    ]
}
```

### Create a user

1. Go to **Administrator** → **Identity** → **Users**
2. Click **Create User +**
3. Enter a username and password (these are console login credentials)
4. Assign the policies you want

### Create access keys

To use MinIO with S3-compatible tools (like AltarSender), users need Access Keys:

**Option 1:** User creates their own
- User logs into the console with their credentials
- Creates an Access Key / Secret Key pair
- Adds them to their environment variables

**Option 2:** Admin creates for user
- Admin creates the key pair in the console
- Transmits the credentials securely to the user

Access Keys inherit the permissions of the user they belong to.

---

### Manage existing users

#### View user details

1. Go to **Administrator** → **Identity** → **Users**
2. Click on a username to see their policies and access keys

#### Grant additional policies

1. Go to **Administrator** → **Identity** → **Users**
2. Click on the username
3. In the **Policies** section, click **Assign Policies**
4. Select the policies to add and click **Save**

#### Revoke policies

1. Go to **Administrator** → **Identity** → **Users**
2. Click on the username
3. In the **Policies** section, click the ✕ next to the policy to remove

#### Delete a user

1. Go to **Administrator** → **Identity** → **Users**
2. Check the box next to the user(s) to delete
3. Click **Delete Selected**

> **Note:** Deleting a user also invalidates all their access keys.

#### Revoke access keys

To revoke access without deleting the user:

1. Go to **Administrator** → **Identity** → **Users**
2. Click on the username
3. In the **Access Keys** section, click the ✕ next to the key to revoke

Or the user can delete their own keys from their dashboard.
