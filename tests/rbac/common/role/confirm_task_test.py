# Copyright 2018 Contributors to Hyperledger Sawtooth
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------
"""Confirm Role Add Task Test"""

# pylint: disable=no-member,too-many-locals

import logging
import pytest

from rbac.common import rbac
from rbac.common import protobuf
from tests.rbac.common import helper
from tests.rbac.common.assertions import TestAssertions

LOGGER = logging.getLogger(__name__)


@pytest.mark.role
class ConfirmRoleAddTaskTest(TestAssertions):
    """Confirm Role Add Task Test"""

    @pytest.mark.library
    def test_make(self):
        """Test making the message"""
        task_id = helper.task.id()
        role_id = helper.role.id()
        proposal_id = helper.proposal.id()
        reason = helper.proposal.reason()
        message = rbac.role.task.confirm.make(
            proposal_id=proposal_id, task_id=task_id, role_id=role_id, reason=reason
        )
        self.assertIsInstance(message, protobuf.role_transaction_pb2.ConfirmAddRoleTask)
        self.assertEqual(message.proposal_id, proposal_id)
        self.assertEqual(message.task_id, task_id)
        self.assertEqual(message.role_id, role_id)
        self.assertEqual(message.reason, reason)

    @pytest.mark.library
    def test_make_addresses(self):
        """Test making the message addresses"""
        task_id = helper.task.id()
        role_id = helper.role.id()
        proposal_id = helper.proposal.id()
        proposal_address = rbac.role.task.propose.address(role_id, task_id)
        reason = helper.proposal.reason()
        relationship_address = rbac.role.task.address(role_id, task_id)
        task_owner_keypair = helper.user.key()
        task_owner_address = rbac.task.owner.address(
            task_id, task_owner_keypair.public_key
        )
        signer_user_address = rbac.user.address(task_owner_keypair.public_key)
        message = rbac.role.task.confirm.make(
            proposal_id=proposal_id, task_id=task_id, role_id=role_id, reason=reason
        )

        inputs, outputs = rbac.role.task.confirm.make_addresses(
            message=message, signer_keypair=task_owner_keypair
        )

        self.assertIsInstance(inputs, list)
        self.assertIn(task_owner_address, inputs)
        self.assertIn(proposal_address, inputs)
        self.assertIn(relationship_address, inputs)
        self.assertIn(signer_user_address, inputs)
        self.assertEqual(len(inputs), 4)

        self.assertIsInstance(outputs, list)
        self.assertIn(proposal_address, outputs)
        self.assertIn(relationship_address, outputs)
        self.assertEqual(len(outputs), 2)

    @pytest.mark.library
    def test_make_payload(self):
        """Test making the message payload"""
        task_id = helper.task.id()
        role_id = helper.role.id()
        proposal_id = helper.proposal.id()
        proposal_address = rbac.role.task.propose.address(role_id, task_id)
        reason = helper.proposal.reason()
        relationship_address = rbac.role.task.address(role_id, task_id)
        task_owner_keypair = helper.user.key()
        task_owner_address = rbac.task.owner.address(
            task_id, task_owner_keypair.public_key
        )
        signer_user_address = rbac.user.address(task_owner_keypair.public_key)
        message = rbac.role.task.confirm.make(
            proposal_id=proposal_id, task_id=task_id, role_id=role_id, reason=reason
        )

        payload = rbac.role.task.confirm.make_payload(
            message=message, signer_keypair=task_owner_keypair
        )
        self.assertIsInstance(payload, protobuf.rbac_payload_pb2.RBACPayload)
        inputs = list(payload.inputs)
        outputs = list(payload.outputs)

        self.assertIsInstance(inputs, list)
        self.assertIn(task_owner_address, inputs)
        self.assertIn(proposal_address, inputs)
        self.assertIn(relationship_address, inputs)
        self.assertIn(signer_user_address, inputs)
        self.assertEqual(len(inputs), 4)

        self.assertIsInstance(outputs, list)
        self.assertIn(proposal_address, outputs)
        self.assertIn(relationship_address, outputs)
        self.assertEqual(len(outputs), 2)

    @pytest.mark.confirm_role_task
    def test_create(self):
        """Test executing the message on the blockchain"""
        proposal, _, _, _, _, _, task_owner_key = helper.role.task.propose.create()

        reason = helper.role.task.propose.reason()
        message = rbac.role.task.confirm.make(
            proposal_id=proposal.proposal_id,
            role_id=proposal.object_id,
            task_id=proposal.related_id,
            reason=reason,
        )
        confirm, status = rbac.role.task.confirm.create(
            signer_keypair=task_owner_key,
            message=message,
            object_id=proposal.object_id,
            related_id=proposal.related_id,
        )
        self.assertStatusSuccess(status)
        self.assertIsInstance(confirm, protobuf.proposal_state_pb2.Proposal)
        self.assertEqual(
            confirm.proposal_type, protobuf.proposal_state_pb2.Proposal.ADD_ROLE_TASK
        )
        self.assertEqual(confirm.proposal_id, proposal.proposal_id)
        self.assertEqual(confirm.object_id, proposal.object_id)
        self.assertEqual(confirm.related_id, proposal.related_id)
        self.assertEqual(confirm.close_reason, reason)
        self.assertEqual(confirm.status, protobuf.proposal_state_pb2.Proposal.CONFIRMED)
        self.assertTrue(
            rbac.role.task.exists(
                object_id=proposal.object_id, related_id=proposal.related_id
            )
        )
