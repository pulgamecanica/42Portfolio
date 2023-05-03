"""
status code:
	- 404 => Not Found, if the internet connection ever fails (intra or ours)
	- 401 => Failed authorization, url build, secret expired
	- 500 => Intra Internal Server Error, intra is down (most likely)
	- 200 => OK 
"""
def intra_fail_reason(dict_key):
	errors_dict = {
		404: "The url requested was not founded",
		401: "Intra rejected your request, bad request, check your parameters",
		500: "Intra is down RIP :(",
		"json": "Wrong json format, format received was different from expected"
	}
	return errors_dict[dict_key] if dict_key in errors_dict else "Unkown error";

