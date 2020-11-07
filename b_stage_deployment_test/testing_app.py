import os
import sys

from os.path import dirname as dn
from aws_cdk.core import App

"""
Import main stack.
"""

sys.path.append(dn(dn(os.path.abspath(__file__))))
from b_stage_deployment_test.testing_infrastructure import TestingInfrastructure

"""
Create CDK app.
"""

app = App()
TestingInfrastructure(app)
app.synth()
