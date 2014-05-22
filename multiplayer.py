client = None
model = None

def console_connect_dialog(start_thread = True):
    global _endpoint
    import multiplayer.connect_dialog as connect_dialog
    endpoint = connect_dialog.console_connect_dialog()
    set_endpoint(endpoint)
    if start_thread:
        import multiplayer.updater as updater
        model.set_updater(updater.ThreadingUpdater)

def set_endpoint(endpoint):
    global client, _endpoint, model
    import multiplayer.client as _client
    import multiplayer.model as _model
    if client is None or client.is_closed():
        client = _client.Client(endpoint)
        model = _model.Model(client)
    else:
        client.set_endpoint(endpoint)
    _endpoint = endpoint

def everywhere(function, *args):
    assert model is not None, 'initialize the model with a connect dialog'
    return model.everywhere(function, *args)
    
