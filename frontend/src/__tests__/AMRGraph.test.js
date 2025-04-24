import { render, screen } from "@testing-library/react";
import AMRGraph from "../components/AMRGraph";

test("renders AMRGraph with stubbed network", () => {
  render(<AMRGraph amrText="(a / test)" />);
  expect(screen.getByTestId("vis-network-stub")).toBeInTheDocument();
});
