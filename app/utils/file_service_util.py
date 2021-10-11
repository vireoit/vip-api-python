ALLOWED_FILE_TYPES = set(['csv', 'xlx', 'xlsx'])

def allowed_document_types(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_TYPES
