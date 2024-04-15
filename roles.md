# Role documentation


## block(id=0)
This role can be used to restrict users so they can't upload any images.
Users with role `block` will be handled like users with role `default` but they are redirected to
an error page whenever they try to upload an image.

## default(id=1)
The `default` role is as the nanme suggesst the role every user is assigned to when registering.
This users get the upload limit defined with `DEFAULT_USER_UPLOAD_LIMIT` in the `.env` file.

## admin(id=9)
An `admin` user is allowed to perform whatever a `default` user is allowed to but can also access the admin area.
The admin dashboard is accessable through `domain.tld/admin/dashboard`.
Admins can change the role of a user and also adjust their upload limits.
Admins have the possibility to approve/remove users files. 
