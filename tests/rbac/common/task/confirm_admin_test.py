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
"""Confirm Task Add Admin Test"""
# pylint: disable=no-member,too-many-locals

import logging
import pytest

from rbac.common import rbac
from rbac.common import protobuf
from tests.rbac.common import helper
from tests.rbac.common.assertions import TestAssertions

LOGGER = logging.getLogger(__name__)


@pytest.mark.task
class ConfirmTaskAddAdminTest(TestAssertions):
    """Confirm Task Add Admin Test"""

    @pytest.mark.library
    def test_make(self):
        """Test making the message"""
        user_id = helper.user.id()
        task_id = helper.task.id()
        proposal_id = helper.proposal.id()
        reason = helper.proposal.reason()
        message = rbac.task.admin.confirm.make(
            proposal_id=proposal_id, user_id=user_id, task_id=task_id, reason=reason
        )
        self.assertIsInstance(
            message, protobuf.task_transaction_pb2.ConfirmAddTaskAdmin
        )
        self.assertEqual(message.proposal_id, proposal_id)
        self.assertEqual(message.user_id, user_id)
        self.assertEqual(message.task_id, task_id)
        self.assertEqual(message.reason, reason)

    @pytest.mark.library
    def test_make_addresses(self):
        """Test making the message addresses"""
        user_id = helper.user.id()
        task_id = helper.task.id()
        proposal_id = helper.proposal.id()
        proposal_address = rbac.task.admin.propose.address(task_id, user_id)
        reason = helper.proposal.reason()
        relationship_address = rbac.task.admin.address(task_id, user_id)
        signer_keypair = helper.user.key()

        user_address = rbac.user.address(user_id)
        signer_admin_address = rbac.task.admin.address(
            task_id, signer_keypair.public_key
        )
        signer_user_address = rbac.user.address(signer_keypair.public_key)
        message = rbac.task.admin.confirm.make(
            proposal_id=proposal_id, user_id=user_id, task_id=task_id, reason=reason
        )

        inputs, outputs = rbac.task.admin.confirm.make_addresses(
            message=message, signer_keypair=signer_keypair
        )

        self.assertIsInstance(inputs, list)
        self.assertIn(user_address, inputs)
        self.assertIn(signer_admin_address, inputs)
        self.assertIn(proposal_address, inputs)
        self.assertIn(relationship_address, inputs)
        self.assertIn(signer_user_address, inputs)
        self.assertEqual(len(inputs), 5)

        self.assertIsInstance(outputs, list)
        self.assertIn(proposal_address, outputs)
        self.assertIn(relationship_address, outputs)
        self.assertEqual(len(outputs), 2)

    @pytest.mark.library
    def test_make_payload(self):
        """Test making the message payload"""
        user_id = helper.user.id()
        task_id = helper.task.id()
        proposal_id = helper.proposal.id()
        proposal_address = rbac.task.admin.propose.address(task_id, user_id)
        reason = helper.proposal.reason()
        relationship_address = rbac.task.admin.address(task_id, user_id)
        signer_keypair = helper.user.key()

        user_address = rbac.user.address(user_id)
        signer_admin_address = rbac.task.admin.address(
            task_id, signer_keypair.public_key
        )
        signer_user_address = rbac.user.address(signer_keypair.public_key)
        message = rbac.task.admin.confirm.make(
            proposal_id=proposal_id, user_id=user_id, task_id=task_id, reason=reason
        )

        payload = rbac.task.admin.confirm.make_payload(
            message=message, signer_keypair=signer_keypair
        )
        self.assertIsInstance(payload, protobuf.rbac_payload_pb2.RBACPayload)
        inputs = list(payload.inputs)
        outputs = list(payload.outputs)

        self.assertIsInstance(inputs, list)
        self.assertIn(user_address, inputs)
        self.assertIn(signer_admin_address, inputs)
        self.assertIn(proposal_address, inputs)
        self.assertIn(relationship_address, inputs)
        self.assertIn(signer_user_address, inputs)
        self.assertEqual(len(inputs), 5)

        self.assertIsInstance(outputs, list)
        self.assertIn(proposal_address, outputs)
        self.assertIn(relationship_address, outputs)
        self.assertEqual(len(outputs), 2)

    @pytest.mark.confirm_task_admin
    def test_create(self):
        """Test executing the message on the blockchain"""
        proposal, _, _, task_admin_key, _, _ = helper.task.admin.propose.create()

        reason = helper.task.admin.propose.reason()
        message = rbac.task.admin.confirm.make(
            proposal_id=proposal.proposal_id,
            task_id=proposal.object_id,
            user_id=proposal.related_id,
            reason=reason,
        )
        _, status = rbac.task.admin.confirm.create(
            signer_keypair=task_admin_key, message=message
        )
        self.assertStatusSuccess(status)
        confirm = rbac.task.admin.confirm.get(
            object_id=proposal.object_id, related_id=proposal.related_id
        )
        self.assertIsInstance(confirm, protobuf.proposal_state_pb2.Proposal)
        self.assertEqual(
            confirm.proposal_type, protobuf.proposal_state_pb2.Proposal.ADD_TASK_ADMIN
        )
        self.assertEqual(confirm.proposal_id, proposal.proposal_id)
        self.assertEqual(confirm.object_id, proposal.object_id)
        self.assertEqual(confirm.related_id, proposal.related_id)
        self.assertEqual(confirm.close_reason, reason)
        self.assertEqual(confirm.status, protobuf.proposal_state_pb2.Proposal.CONFIRMED)
        self.assertTrue(
            rbac.task.admin.exists(
                object_id=proposal.object_id, related_id=proposal.related_id
            )
        )
