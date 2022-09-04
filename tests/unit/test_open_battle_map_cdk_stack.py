import aws_cdk as core
import aws_cdk.assertions as assertions

from open_battle_map_cdk.open_battle_map_cdk_stack import OpenBattleMapCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in open_battle_map_cdk/open_battle_map_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = OpenBattleMapCdkStack(app, "open-battle-map-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
