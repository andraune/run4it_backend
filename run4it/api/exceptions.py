"""Functions for reporting errors"""
from flask_restful import Api, Resource, abort


def report_error_and_abort(http_code, error_name, error_description):
    abort(int(http_code), errors={str(error_name):[str(error_description)]})
