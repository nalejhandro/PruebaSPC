def doUpload(
        client_email, keyfile, user, filename, mimetype,
        title=None, description=None, parent_id=None):

    import os
    from tools.upload_file import createDriveService
    from tools.upload_file import insertFile
    from httplib2 import ServerNotFoundError
    from apiclient.errors import ResumableUploadError

    try:
        if title is None:
            title = os.path.basename(filename)
        if description is None:
            description = ''

        service = createDriveService(client_email, keyfile, user)
        file_metadata = insertFile(
            service, filename, title,
            mimetype, description=description, parent_id=parent_id)
        print('File Uploaded')

    except FileNotFoundError as e:
        print('Unable to read the keyfile: {0}'.format(e))

    except ServerNotFoundError as e:
        print('Unable to build the service: {0}'.format(e))

    except ResumableUploadError as e:
        print('Unable upload the file: {0}'.format(e))


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Upload file to google drive')
    parser.add_argument('account', help='Client email for the service account')
    parser.add_argument('keyfile', help='Path to the key file provided by Google App Engine')
    parser.add_argument('user', help='Email of the user to impersonate')
    parser.add_argument('file', help='Path of the file to upload')
    parser.add_argument('mimetype', help='File mime type')
    parser.add_argument('--title', nargs='?',
        help='Title of the file after upload')
    parser.add_argument('--desc', nargs='?',
        help='File description')
    parser.add_argument('--parent', nargs='?',
        help='Parent folder to store the uploaded file')
    args = parser.parse_args()
    doUpload(
        args.account, args.keyfile, args.user, args.file,
        args.mimetype, args.title, args.desc, args.parent)
