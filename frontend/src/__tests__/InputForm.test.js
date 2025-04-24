import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import InputForm from "../InputForm";

test("renders summary and article inputs", () => {
  render(
    <MemoryRouter>
      <InputForm />
    </MemoryRouter>
  );
  expect(screen.getByLabelText(/summary/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/article/i)).toBeInTheDocument();
});
