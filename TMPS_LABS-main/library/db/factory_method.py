class WrongQueryType(BaseException):
    pass

class QueryInterface:
    def __init__(self, params, params_order):
        self.params = params
        self.params_order = params_order

    def generate_query(self):
        pass

class MessageInsertQuery(QueryInterface):
    def generate_query(self):
        param_order = [self.params[param] for param in self.params_order]
        return tuple(param_order)

class UserInsertQuery(QueryInterface):
    def generate_query(self):
        param_order = [self.params[param] for param in self.params_order]
        return tuple(param_order)

class QueryCreator:
    def __init__(self, order):
        self.order = order

    def create_query(self, json_data):
        pass

class MessageInsertQueryCreator(QueryCreator):
    def create_query(self, json_data):
        if json_data['query-type'] == 'message-insert':
            return MessageInsertQuery(json_data['params'], self.order)
        else:
            raise WrongQueryType("Massage Insert Query can take only queries for inserting messages in Data Base")

class UserInsertQueryCreator(QueryCreator):
    def create_query(self, json_data):
        if json_data['query-type'] == 'user-insert':
            return UserInsertQuery(json_data['params'], self.order)
        else:
            raise WrongQueryType("User Insert Query can take only queries for inserting users in Data Base")
