#!/usr/bin/python

import pymssql
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.parsing.convert_bool import BOOLEANS

def execute_query(module, db_connection, dict_list):
    """Execute a SQL query."""

    query = module.params['query']

    fetch_rec = []
    try:
        connection_cursor = db_connection.cursor(as_dict=dict_list)
        connection_cursor.execute(query)
        try:
            fetch_rec = connection_cursor.fetchall()
        except pymssql.OperationalError as OpExc:
            if 'Statement not executed or executed statement has no resultset' in OpExc.args:
                pass
        check_updated = connection_cursor.rowcount != 0
        db_connection.commit()
        connection_cursor.close()
    except pymssql.ColumnsWithoutNamesError as ex:
        return execute_query(module, db_connection, False)
    except pymssql.Error as ex:
        if ex.args:
            module.fail_json(msg='Unable to execute query: {}'.format(ex[1]), errno=ex[0])
        module.fail_json(msg='Unable to execute query: {}'.format(ex))
    finally:
        if db_connection is not None:
            db_connection.close()

    return (check_updated, fetch_rec, connection_cursor.rowcount)


def main():
    module = AnsibleModule
    (
        argument_spec={
            'login_host': {'type': 'str', 'default': ''},
            'port': {'type': 'int', 'default': 1433, 'aliases': ['login_port']},
            'login_user': {'type': 'str', 'default': ''},
            'login_password': {'type': 'str', 'default': '', 'no_log': True},
            'query': {'required': True, 'type': 'str'},
            'db': {'type': 'str', 'default': ''},
            'autocommit': {'type': 'bool', 'choices': BOOLEANS, 'default': False},
            'tds_version': {'type': 'str', 'default': '7.1'},
            'dict_list': {'type': 'bool', 'choices': BOOLEANS, 'default': False},
        }
    )


    try:
        db_connection = pymssql.connect(host=module.params['login_host'],
                                        port=str(module.params['port']),
                                        user=module.params['login_user'],
                                        password=module.params['login_password'],
                                        database=module.params['db'],
                                        tds_version=module.params['tds_version'])
        db_connection.autocommit(module.params['autocommit'])
    except pymssql.Error as ex:
        module.fail_json(msg='Unable to connect to database: {}'.format(ex))

    (check_updated, fetch_rec, rowcount) = execute_query(module, db_connection,
                                            dict_list=module.params['dict_list'])

    module.exit_json(changed=check_updated, result=fetch_rec, rowcount=rowcount,msg=rowcount)


if __name__ == '__main__':
    main()

