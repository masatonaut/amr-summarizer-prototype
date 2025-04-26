import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import InputForm from "../InputForm";

test("renders summary and article inputs", () => {
  /**
   * Component test:
   * InputForm uses React Router's useNavigate hook,
   * so we wrap it in a MemoryRouter for proper context.
   * Verifies that both Summary and Article text fields are rendered.
   */
  render(
    <MemoryRouter>
      <InputForm />
    </MemoryRouter>
  );
  // Check that the form labels exist
  expect(screen.getByLabelText(/summary/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/article/i)).toBeInTheDocument();
});
