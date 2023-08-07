from aws_cdk.aws_apigatewayv2 import CfnApi, CfnStage, CfnRoute, CfnIntegration
from aws_cdk.aws_lambda import Function, Code, Runtime
from b_aws_testing_framework.tools.cdk_testing.testing_manager import TestingManager
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack
from constructs import Construct

from b_stage_deployment.function import StageDeploymentSingletonFunction
from b_stage_deployment.resource import StageDeploymentResource


class TestingInfrastructure(TestingStack):
    """
    This is an entry point for your infrastructure. Create other resources and stacks you want to test here.
    """

    def __init__(self, scope: Construct):
        super().__init__(scope=scope)

        prefix = TestingManager.get_global_prefix()

        api = CfnApi(
            scope=self,
            id=f'{prefix}Api',
            description='Sample API.',
            name=f'{prefix}Api',
            protocol_type='HTTP'
        )

        stage = CfnStage(
            scope=self,
            id=f'{prefix}Stage',
            api_id=api.ref,
            stage_name='prod',
            auto_deploy=False,
            description='Test description.'
        )

        function = Function(
            scope=self,
            id=f'{prefix}TestFunction',
            function_name=f'{prefix}TestFunction',
            code=Code.from_inline(
                'def handler(*args, **kwargs):\n'
                '    return {\n'
                '        "isBase64Encoded": False,\n'
                '        "statusCode": 200,\n'
                '        "headers": {},\n'
                '        "body": "{\\"message\\": \\"success\\"}"\n'
                '    }\n'
            ),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_8,
        )

        integration = CfnIntegration(
            scope=self,
            id=f'{prefix}LambdaIntegration',
            api_id=api.ref,
            integration_type='AWS_PROXY',
            integration_uri=(
                f'arn:aws:apigateway:{self.region}:lambda:path/2015-03-31'
                f'/functions/{function.function_arn}/invocations'
            ),
            description='Sample lambda proxy integration.',
            payload_format_version='1.0'
        )

        CfnRoute(
            scope=self,
            id=f'{prefix}SampleRoute',
            api_id=api.ref,
            route_key='GET /test',
            target=f'integrations/{integration.ref}'
        )

        backend = StageDeploymentSingletonFunction(self, f'{prefix}DeploymentBackend')

        # Make some deployments.
        StageDeploymentResource(self, 'C1', backend, api.ref, stage.stage_name, 'Sample1.')
        StageDeploymentResource(self, 'C2', backend, api.ref, stage.stage_name, 'Sample2.')
        StageDeploymentResource(self, 'C3', backend, api.ref, stage.stage_name, 'Sample3.')
        StageDeploymentResource(self, 'C4', backend, api.ref, stage.stage_name, 'Sample4.')
        StageDeploymentResource(self, 'C5', backend, api.ref, stage.stage_name, 'Sample5.')

        self.add_output('ApiId', api.ref)
        self.add_output('StageName', stage.stage_name)
