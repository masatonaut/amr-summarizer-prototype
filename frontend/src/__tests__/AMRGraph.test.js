import React from "react";
import { render, screen } from "@testing-library/react";
import AMRGraph from "../components/AMRGraph";

test("renders AMRGraph with stubbed network", () => {
  /**
   * Component test:
   * We stub out the vis-network internals so that AMRGraph
   * should render a placeholder element with data-testid="vis-network-stub".
   */
  render(<AMRGraph amrText="(a / test)" />);
  expect(screen.getByTestId("vis-network-stub")).toBeInTheDocument();
});
