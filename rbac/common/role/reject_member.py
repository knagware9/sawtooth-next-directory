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
"""Implements the REJECT_ADD_ROLE_MEMBER message
usage: rbac.role.member.reject.create()"""
import logging
from rbac.common import addresser
from rbac.common.crypto.keys import Key
from rbac.common.proposal.proposal_reject import ProposalReject

LOGGER = logging.getLogger(__name__)


class RejectAddRoleMember(ProposalReject):
    """Implements the REJECT_ADD_ROLE_MEMBER message
    usage: rbac.role.member.reject.create()"""

    def __init__(self):
        super().__init__()
        self._register()

    @property
    def message_action_type(self):
        """The action type performed by this message"""
        return addresser.MessageActionType.REJECT

    @property
    def message_subaction_type(self):
        """The subsequent action performed or proposed by this message"""
        return addresser.MessageActionType.ADD

    @property
    def message_object_type(self):
        """The object type this message acts upon"""
        return addresser.ObjectType.ROLE

    @property
    def message_related_type(self):
        """the object type of the related object this message acts upon"""
        return addresser.ObjectType.USER

    @property
    def message_relationship_type(self):
        """The relationship type this message acts upon"""
        return addresser.RelationshipType.MEMBER

    def make_addresses(self, message, signer_keypair):
        """Makes the appropriate inputs & output addresses for the message"""
        if not isinstance(message, self.message_proto):
            raise TypeError("Expected message to be {}".format(self.message_proto))
        if not isinstance(signer_keypair, Key):
            raise TypeError("Expected signer_keypair to be provided")

        # should be owner not admin
        signer_admin_address = addresser.role.admin.address(
            message.role_id, signer_keypair.public_key
        )
        signer_owner_address = addresser.role.owner.address(
            message.role_id, signer_keypair.public_key
        )
        signer_user_address = addresser.user.address(signer_keypair.public_key)

        proposal_address = self.address(
            object_id=message.role_id, related_id=message.user_id
        )

        inputs = [
            proposal_address,
            signer_admin_address,
            signer_owner_address,
            signer_user_address,
        ]
        outputs = [proposal_address]

        return inputs, outputs

    def validate_state(self, context, message, inputs, input_state, store, signer):
        """Validates that:
        1. the signer is an owner of the role"""
        super().validate_state(
            context=context,
            message=message,
            inputs=inputs,
            input_state=input_state,
            store=store,
            signer=signer,
        )
        if not addresser.role.owner.exists_in_state_inputs(
            inputs=inputs,
            input_state=input_state,
            object_id=message.role_id,
            related_id=signer,
        ):
            raise ValueError(
                "Signer {} must be an owner of the role {}".format(
                    signer, message.role_id
                )
            )
