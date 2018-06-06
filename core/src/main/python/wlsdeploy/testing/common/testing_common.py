"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import VariableException

# python classes from weblogic-deploy-tooling
from wlsdeploy.util import variables

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.exception import exception_helper

_class_name = 'testing_common'


def apply_substitution_variables_file(variable_file, model_dict, logger):
    _method_name = 'apply_substitution_variables_file'

    if variable_file is None:
        return

    try:
        variable_map = variables.load_variables(variable_file)
        variables.substitute(model_dict, variable_map)
    except VariableException, ve:
        ex = exception_helper.create_testing_exception('WLSDPLY-09814',
                                                       variable_file,
                                                       ve.getLocalizedMessage(), error=ve)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex
