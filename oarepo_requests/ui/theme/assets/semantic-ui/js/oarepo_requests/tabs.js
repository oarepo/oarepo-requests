// Copyright (c) 2026 CESNET
// SPDX-License-Identifier: MIT

import $ from "jquery";

const QUERY_PARAM = "tab";
const $menu = $("#request-community-submission-tab");

if ($menu.length) {
  const params = new URLSearchParams(window.location.search);
  const tabName = params.get(QUERY_PARAM);
  if (tabName && $menu.find(`.item[data-tab="${tabName}"]`).length) {
    $menu.find(".item").tab("change tab", tabName);
  }

  $menu.find(".item").on("click", function () {
    const clicked = $(this).attr("data-tab");
    if (!clicked) return;
    const url = new URL(window.location.href);
    url.searchParams.set(QUERY_PARAM, clicked);
    window.history.replaceState(null, "", url.toString());
  });
}
