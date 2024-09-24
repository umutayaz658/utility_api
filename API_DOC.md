# CUSTOM TOKEN API

## Obtain Custom Token

### URL
`/api/token/`

### Method
`POST`

### Description
Authenticates a user and returns a pair of access and refresh tokens, including the username in the token payload.

### Request Parameters

| Parameter Name | Type   | Required | Description           |
|----------------|--------|----------|-----------------------|
| username       | String | Yes      | The username of the user |
| password       | String | Yes      | The password for the user |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

## Refresh Custom Token

### URL
`/api/token/refresh/`

### Method
`POST`

### Description
Accepts a refresh token and returns a new access token.

### Request Parameters

| Parameter Name | Type   | Required | Description           |
|----------------|--------|----------|-----------------------|
| refresh        | String | Yes      | The refresh token to be used for obtaining a new access token |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "access": "your_new_access_token"
}
```


## Blacklist Custom Token

### URL
`/api/logout/`

### Method
`POST`

### Description
Logs out the user by blacklisting the provided refresh token.

### Request Parameters

| Parameter Name | Type   | Required | Description           |
|----------------|--------|----------|-----------------------|
| refresh        | String | Yes      | The refresh token to be blacklisted |

### Successful Response

**Status Code:** `205 Reset Content`

### Error Responses

- **400 Bad Request**: Invalid or missing refresh token.
```json
  {
    "error": "Invalid token"
  }
```

# USER REGISTRATION AND AUTHENTICATION API

This API provides basic user session management, including user registration, login, and logout functionalities.

## User Registration

### URL
`/register/`

### Method
`POST`

### Description
Creates a new user in the system.

### Request Parameters

| Parameter Name | Type   | Required | Description           |
|----------------|--------|----------|-----------------------|
| username       | String | Yes      | The username of the user |
| password       | String | Yes      | The password for the user |

### Successful Response

**Status Code:** `201 Created`

**Response Body:**
```json
{
  "message": "User created successfully"
}
```


## User Login

### URL
`/login/`

### Method
`POST`

### Description
Logs in an existing user by validating their credentials.

### Request Parameters

| Parameter Name | Type   | Required | Description           |
|----------------|--------|----------|-----------------------|
| username       | String | Yes      | The username of the user |
| password       | String | Yes      | The password for the user |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "message": "Login successful"
}
```


## User Logout

### URL
`/logout/`

### Method
`POST`

### Description
Logs out the currently authenticated user.

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "message": "Logged out successfully"
}
```


# URL SHORTENER API

## Create Short URL 

### URL
`/api/shorten-url/`

### Method
`POST`

### Description
Creates a short URL based on the provided long URL and other parameters.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Request Parameters

| Parameter Name    | Type     | Required | Description                                 |
|-------------------|----------|----------|---------------------------------------------|
| long_url          | String   | Yes      | The original long URL to be shortened       |
| validity_period    | Integer  | Yes      | The period (in days) for which the short URL is valid |
| is_active         | Boolean  | Yes      | Indicates if the short URL is active       |
| one_time_only     | Boolean  | Yes      | Indicates if the short URL can only be used once |
| password          | String   | No       | Password required to access the short URL   |

### Successful Response

**Status Code:** `201 Created`

**Response Body:**
```json
{
  "short_url": "your_short_url"
}
```


## URL Detail

### URL
`/api/url-details/`

### Method
`GET`

### Description
Retrieves a list of short URLs created by the authenticated user, along with their details.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "short_url": "your_short_url",
  "long_url": "original_long_url",
  "created_at": "YYYY-MM-DD HH:mm",
  "validity_period": "YYYY-MM-DD HH:mm",
  "created_by": "username",
  "is_active": true,
  "one_time_only": false,
  "password": "optional_password",
  "is_deleted": false
}
```


## Get Long URL

### URL
`/api/get-long-url/`

### Method
`POST`

### Description
Retrieves the original long URL associated with a given short URL. This endpoint requires the user to be authenticated and may require a password if the URL is protected.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Request Parameters

| Parameter Name | Type   | Required | Description                     |
|----------------|--------|----------|---------------------------------|
| short_url      | String | Yes      | The short URL to be resolved    |
| password       | String | No       | The password for the short URL, if applicable |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "long_url": "original_long_url"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "error": "short_url is required"
}
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Status Code:** `403 Forbidden`

**Response Body:**
```json
{
  "error": "Invalid password"
}
```

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "error": "URL not found"
}
```

**Status Code:** `500 Internal Server Error`

**Response Body:**
```json
{
  "error": "An unexpected error occurred"
}
```


## Update URL Active Status

### URL
`/api/update-url-status/<short_url>/`

### Method
`PUT`

### Description
Updates the active status of a short URL.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Request Parameters

| Parameter Name | Type     | Required | Description                               |
|----------------|----------|----------|-------------------------------------------|
| is_active      | Boolean  | Yes      | Indicates if the short URL should be active or inactive |

### Path Parameters

| Parameter Name | Type     | Required | Description                               |
|----------------|----------|----------|-------------------------------------------|
| short_url      | String   | Yes      | The short URL to update                  |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "message": "URL status updated successfully"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "error": "is_active is required"
}
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "error": "URL not found"
}
```

## Delete URL

### URL
`/api/delete-url/<short_url>/`

### Method
`PUT`

### Description
Marks a short URL as deleted.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Request Parameters

| Parameter Name | Type     | Required | Description                               |
|----------------|----------|----------|-------------------------------------------|
| is_deleted      | Boolean  | Yes      | Indicates if the short URL should be marked as deleted or not |

### Path Parameters

| Parameter Name | Type     | Required | Description                               |
|----------------|----------|----------|-------------------------------------------|
| short_url      | String   | Yes      | The short URL to mark as deleted         |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "message": "URL deleted successfully"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "error": "is_deleted is required"
}
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "error": "URL not found"
}
```

## Update Validity Period

### URL
`/api/update-validity-period/<short_url>/`

### Method
`PUT`

### Description
Updates the validity period of a short URL.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Request Parameters

| Parameter Name   | Type     | Required | Description                               |
|------------------|----------|----------|-------------------------------------------|
| validity_period   | String   | Yes      | The new validity period in ISO 8601 format (e.g., "2023-12-31T23:59:59Z") |

### Path Parameters

| Parameter Name | Type     | Required | Description                               |
|----------------|----------|----------|-------------------------------------------|
| short_url      | String   | Yes      | The short URL for which to update the validity period |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "message": "Validity period updated successfully"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "error": "validity_period field is required"
}
```
```json
{
  "error": "Invalid date format for validity_period"
}
```
```json
{
  "error": "Validity period cannot be in the past."
}
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "error": "URL not found"
}
```

# QUICK NOTE API

## Create Quick Note

### URL
`/api/quick-notes/`

### Method
`POST`

### Description
Creates a new quick note that can be sent to another user.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Request Parameters

| Parameter Name | Type     | Required | Description                                      |
|----------------|----------|----------|--------------------------------------------------|
| send_to        | String   | Yes      | The username of the user to whom the note is sent |
| text           | String   | No       | The text content of the note (optional; defaults to an empty string if None) |
| file           | File     | No       | An optional file to attach to the note           |

### Successful Response

**Status Code:** `201 Created`

**Response Body:**
```json
{
  "id": 1,
  "created_at": "2024-09-23 12:34",
  "created_by": "your_username",
  "send_to": "recipient_username",
  "text": "Decrypted text content",
  "file": null,
  "file_download_url": "http://167.71.39.190:8000/api/notes/download/1/"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "send_to": "User with this username does not exist."
}
```
```json
{
  "text": "Invalid input for text."
}
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

## List User Sent Notes

### URL
`/api/quick-notes/sent/`

### Method
`GET`

### Description
Retrieves a list of quick notes sent by the authenticated user.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{    
    "id": 1,
    "created_at": "2024-09-23 12:34",
    "created_by": "your_username",        
    "text": "Decrypted text content",    
    "file": null,
    "send_to": "recipient_username"
}     
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "error": "No notes found."
}
```

## List User Received Notes

### URL
`/api/quick-notes/received/`

### Method
`GET`

### Description
Retrieves a list of quick notes received by the authenticated user.

### Authentication
This endpoint requires a Bearer token. Include the token in the `Authorization` header.

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{    
    "id": 1,
    "created_at": "2024-09-23 12:34",
    "created_by": "your_username",        
    "text": "Decrypted text content",    
    "file": null,
    "send_to": "recipient_username"
}     
```

**Status Code:** `401 Unauthorized`

**Response Body:**
```json
{
  "error": "Authentication credentials were not provided."
}
```

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "error": "No notes found."
}
```

## Quick Note File Download

### URL
`/api/notes/download/{note_id}/`

### Method
`GET`

### Description
Downloads the file attached to the specified quick note. If no file is attached or the file does not exist, an error is returned.

### URL Parameters

| Parameter Name | Type   | Required | Description                         |
|----------------|--------|----------|-------------------------------------|
| note_id        | Integer| Yes      | The ID of the quick note            |

### Successful Response

**Status Code:** `200 OK`

**Response:** The attached file will be downloaded.

**Response Headers:**

**Status Code:** `404 Not Found`

**Response Body:**
```json
{
  "send_to": "No file attached to this note."
}
```
```json
{
  "text": "File does not exist."
}
```

## User Autocomplete

### URL
`/api/users/autocomplete/`

### Method
`GET`

### Description
Returns a list of up to 10 users whose usernames start with the given query string for autocomplete purposes.

### Query Parameters

| Parameter Name | Type   | Required | Description                              |
|----------------|--------|----------|------------------------------------------|
| send_to        | String | Yes      | The query string to search for usernames |

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
[
  {
    "username": "exampleuser1"
  },
  {
    "username": "exampleuser2"
  }
]
```

# QR CODE API

## Create QR Code

### URL
`/api/qr-code/`

### Method
`POST`

### Description
Generates a QR code based on the provided data. Optionally returns a download link for the QR code image file.

### Request Body

| Field         | Type    | Required | Description                                                |
|---------------|---------|----------|------------------------------------------------------------|
| data          | String  | Yes      | The data to be encoded in the QR code.                     |
| download_link | Boolean | No       | If `true`, a download link for the QR code image is returned. If `false` or not provided, the QR code image is returned directly in the response. |

### Successful Responses

1. **QR Code Image Returned:**

**Status Code:** `200 OK`

**Response Headers:**

**Response Body:** QR code image as `image/png`.

2. **Download Link Returned:**

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "download_url": "http://example.com/api/download-qr-code/qrcodefilename.png"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "error": "No data provided."
}
```

# IMAGE TO PDF API

## Convert Image to PDF

### URL
`/api/imagetopdf/`

### Method
`POST`

### Description
Converts a list of image files into a single PDF file and returns a download URL for the generated PDF.

### Request Body

| Field        | Type      | Required | Description                                   |
|--------------|-----------|----------|-----------------------------------------------|
| image_paths  | List      | Yes      | A list of image file paths to be converted to PDF. |

**Example Request Body (Form Data):**
```json
{
  "image_paths": ["path/to/image1.jpg", "path/to/image2.png"]
}
```

### Successful Response

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "download_url": "http://example.com/api/download-qr-code/qrcodefilename.png"
}
```

**Status Code:** `400 Bad Request`

**Response Body:**
```json
{
  "error": "Select an image."
}
```
```json
{
  "error": "Error: <specific error message>"
}
```

