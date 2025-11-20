# Class Bundle Communications, Tickets, and File Uploads

## Overview

Class bundles now support full communication capabilities:
- **Messages & Threads**: Writers, clients, admins, editors, and superadmins can communicate
- **Support Tickets**: Clients can create tickets related to their class bundles
- **File Uploads**: All roles can upload files related to class bundles

## Communication Threads

### Creating a Thread

**API Endpoint:** `POST /api/v1/class-management/class-bundles/{id}/create_thread/`

**Request Body:**
```json
{
    "recipient_id": 123,
    "subject": "Question about assignment",
    "initial_message": "Can you clarify the requirements?"
}
```

**Permissions:**
- Client (bundle owner)
- Assigned writer
- Staff (admin/editor/superadmin)

**Process:**
1. Validates user has access to bundle
2. Creates `CommunicationThread` with `thread_type='class_bundle'`
3. Links thread to bundle via GenericForeignKey (`content_type` + `object_id`)
4. Adds participants (client, recipient, assigned writer if exists)
5. Optionally creates initial message

### Sending Messages

Messages can be sent via the standard communication API:

**API Endpoint:** `POST /api/v1/communications/threads/{thread_id}/messages/`

**Request Body:**
```json
{
    "recipient_id": 123,
    "message": "Message text here",
    "message_type": "text",
    "attachment": <file>  // Optional file attachment
}
```

**File Attachments:**
- Messages support file attachments via `CommunicationMessage.attachment`
- Files are stored at `message_attachments/`
- Accessible by all thread participants

### Viewing Threads

**API Endpoint:** `GET /api/v1/class-management/class-bundles/{id}/threads/`

Returns all communication threads for the bundle that the user can access.

## Support Tickets

### Creating a Ticket

**API Endpoint:** `POST /api/v1/class-management/class-bundles/{id}/create_ticket/`

**Request Body:**
```json
{
    "title": "Issue with class materials",
    "description": "Detailed description of the issue",
    "priority": "medium",  // low, medium, high, critical
    "category": "technical"  // general, payment, technical, feedback, order, other
}
```

**Permissions:**
- Client (bundle owner)
- Staff

**Process:**
1. Validates user can create ticket for bundle
2. Creates `Ticket` record
3. Links to bundle via GenericForeignKey (`content_type` + `object_id`)
4. Adds bundle reference to description

### Adding Messages to Tickets

Use the standard ticket messages API:

**API Endpoint:** `POST /api/v1/tickets/{ticket_id}/messages/`

**Request Body:**
```json
{
    "message": "Additional information",
    "is_internal": false  // true for admin-only messages
}
```

### Attaching Files to Tickets

**API Endpoint:** `POST /api/v1/tickets/{ticket_id}/attachments/`

**Request:** multipart/form-data
```
file: <file>
```

**Permissions:**
- Ticket creator
- Staff

### Viewing Tickets

**API Endpoint:** `GET /api/v1/class-management/class-bundles/{id}/tickets/`

Returns all tickets related to the bundle that the user can access.

## File Uploads

### Uploading Files

**API Endpoint:** `POST /api/v1/class-management/class-bundles/{id}/upload_file/`

**Request:** multipart/form-data
```
file: <file>
description: "Optional description"
```

**Permissions:**
- Client (bundle owner)
- Assigned writer
- Staff

**Process:**
1. Validates user has access to bundle
2. Creates `ClassBundleFile` record
3. Stores file at `class_bundles/files/`
4. Sets visibility flags (default: visible to both client and writer)

### File Visibility

Files can be marked as:
- `is_visible_to_client`: Whether client can see the file
- `is_visible_to_writer`: Whether writer can see the file

**Note:** Staff can always see all files.

### Viewing Files

**API Endpoint:** `GET /api/v1/class-management/class-bundles/{id}/files/`

Returns all files for the bundle filtered by visibility:
- Client sees: `is_visible_to_client=True`
- Writer sees: `is_visible_to_writer=True`
- Staff sees: All files

### File Information

Each file includes:
- `id`: File ID
- `file_name`: Original filename
- `file_size`: File size in bytes
- `description`: Optional description
- `uploaded_by`: User who uploaded
- `uploaded_at`: Upload timestamp
- `file_url`: URL to download file

## Models

### ClassBundleFile

```python
class ClassBundleFile(models.Model):
    class_bundle = ForeignKey(ClassBundle)
    uploaded_by = ForeignKey(User)
    file = FileField(upload_to='class_bundles/files/')
    file_name = CharField()
    file_size = PositiveIntegerField()
    description = TextField()
    is_visible_to_client = BooleanField(default=True)
    is_visible_to_writer = BooleanField(default=True)
    uploaded_at = DateTimeField(auto_now_add=True)
```

### CommunicationThread Updates

- Added `content_type` and `object_id` for GenericForeignKey
- `thread_type='class_bundle'` supports class bundle threads
- `order` FK is now nullable (not required for class bundles)

### Ticket Updates

- Added `content_type` and `object_id` for GenericForeignKey
- Can link to orders, class bundles, or other object types

## Permissions Summary

### Communication Threads
- **Create Thread**: Client, assigned writer, staff
- **Send Messages**: Thread participants only
- **View Threads**: Participants and staff

### Support Tickets
- **Create Ticket**: Client, staff
- **View Tickets**: Ticket creator, staff
- **Add Messages**: Ticket creator, staff
- **Attach Files**: Ticket creator, staff

### File Uploads
- **Upload**: Client, assigned writer, staff
- **View**: Based on visibility flags + staff always sees all

## Integration Points

### ClassBundle Model

```python
class ClassBundle(models.Model):
    assigned_writer = ForeignKey(User, limit_choices_to={'role': 'writer'})
    message_threads = GenericRelation(CommunicationThread)
    support_tickets = GenericRelation(Ticket)
    files = Reverse relation to ClassBundleFile
```

### Bundle Serializer

The `ClassBundleSerializer` now includes:
- `files`: List of file attachments
- `threads_count`: Number of communication threads
- `tickets_count`: Number of support tickets
- `assigned_writer_username`: Writer username for display

## Workflow Example

1. **Admin creates bundle** with assigned writer
2. **Client creates ticket** about class materials
3. **Admin responds** via ticket message
4. **Writer creates thread** to communicate with client about assignments
5. **Client uploads file** (assignment requirements)
6. **Writer uploads file** (completed work)
7. **All parties** can see files based on visibility settings

## Access Control

### Writers
- Can access bundles they are assigned to
- Can create threads with client
- Can upload files
- Can see files visible to writers

### Clients
- Can access their own bundles
- Can create tickets
- Can create threads with writer/staff
- Can upload files
- Can see files visible to clients

### Staff (Admin/Editor/Superadmin)
- Can access all bundles
- Can create threads
- Can create/manage tickets
- Can upload files
- Can see all files

All communications and file uploads respect the bundle's access permissions while allowing flexible collaboration between clients, writers, and staff.

