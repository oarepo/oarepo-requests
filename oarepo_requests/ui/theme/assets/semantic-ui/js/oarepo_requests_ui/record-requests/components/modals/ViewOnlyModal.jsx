import React from "react";

import { NewRequestModal, RequestModalContent } from "..";
import { REQUEST_TYPE } from "../../utils/objects";
import { useRequestModal } from "../../utils/hooks";

export const ViewOnlyModal = ({ request, requestType, triggerElement, modalHeader }) => {
  const {
    isOpen: isModalOpen,
    close: closeModal,
    open: openModal
  } = useRequestModal();

  return (
    <NewRequestModal
      header={modalHeader}
      isOpen={isModalOpen}
      closeModal={closeModal}
      openModal={openModal}
      trigger={triggerElement}
      content={
        <RequestModalContent request={request} requestType={requestType} requestModalType={REQUEST_TYPE.ACCEPT} />
      }
    />
  );
}
