export interface Request {
  name: string;
  description: string;
  uuid: string;
  type: string;
  links: Links;
  created_by: Creator;
  receiver: Receiver;
  topic: Receiver;
  created: string; // Datetime
  updated: string; // Datetime
  events?: Event[];
}

export interface Links {
  actions?: RequestActions;
  self: string;
  self_html?: string;
  events?: string;
}

export interface RequestActions {
  create?: string;
  submit?: string;
  cancel?: string;
  accept?: string;
  decline?: string;
  expire?: string;
  delete?: string;
}

export interface Creator {
  reference: string;
  type: string;
  label: string;
  link: string;
}

export interface Receiver {
  reference: Reference;
  type: Type;
  label: Label;
  link: string;
}

export interface Reference {
  id: string;
}

export interface RequestType {
  name: string;
  description: string;
  id: string;
  links: Links;
  fast_approve?: boolean;
  payload_ui?: PayloadUI[];
  event_types?: EventType[];
}

export interface PayloadUI {
  section: string;
  fields: Field[];
}

export interface Field {
  field: string;
  ui_widget: "Input" | "NumberInput" | "MultiInput" | "RichInput" | "TextArea" | "Dropdown" | "AutocompleteDropdown" | "BooleanCheckbox";
  visible: ("requestor" | "approver")[];
  editable: ("requestor" | "approver")[];
  props: React.ComponentProps<any>;
}

export interface EventType {
  name: string;
  description: string;
  id: string;
  links: Links;
  payload_ui?: PayloadUI[];
}

export interface Event {
  payload: any;
  created: string; // Datetime
  created_by: Creator;
  updated: string; // Datetime
  revision_id: number;
  id: string;
  type_code: string;
  type: string;
  links: Links;
  permissions: Permissions;
}

export interface Permissions {
  can_update_comment: boolean;
  can_delete_comment: boolean;
}

export enum RequestTypeEnum {
  CREATE = "create",
  SUBMIT = "submit",
  CANCEL = "cancel",
  ACCEPT = "accept",
  DECLINE = "decline",
  SAVE = "save",
}
