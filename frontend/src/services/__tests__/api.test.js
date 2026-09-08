import { describe, expect, it } from "vitest";
import { extractErrorMessage } from "../api";

describe("extractErrorMessage", () => {
  it("returns a network error message when there is no response", () => {
    expect(extractErrorMessage({})).toMatch(/network/i);
  });

  it("extracts the first field error from a validation error body", () => {
    const error = {
      response: {
        data: {
          success: false,
          message: "Validation failed",
          errors: { email: ["A user with this email already exists."] },
        },
      },
    };
    expect(extractErrorMessage(error)).toBe("A user with this email already exists.");
  });

  it("falls back to the top-level message when errors is empty", () => {
    const error = {
      response: { data: { success: false, message: "Invalid email or password.", errors: {} } },
    };
    expect(extractErrorMessage(error)).toBe("Invalid email or password.");
  });
});
