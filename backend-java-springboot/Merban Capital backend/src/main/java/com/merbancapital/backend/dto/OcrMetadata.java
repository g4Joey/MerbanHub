package com.merbancapital.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OcrMetadata {
    @NotBlank(message = "Original file name is required")
    @Size(max = 255, message = "Original file name must not exceed 255 characters")
    private String originalFileName;

    @NotBlank(message = "New file name is required")
    @Size(max = 255, message = "New file name must not exceed 255 characters")
    private String newFileName;

    @NotBlank(message = "Client name is required")
    @Size(max = 100, message = "Client name must not exceed 100 characters")
    private String clientName;

    @Pattern(regexp = "^[0-9]{1,20}$", message = "Account number must contain only digits")
    private String accountNumber;

    @NotNull(message = "Status is required")
    @Pattern(regexp = "^(FULLY_INDEXED|PARTIAL_INDEXED|FAILED)$",
            message = "Status must be FULLY_INDEXED, PARTIAL_INDEXED, or FAILED")
    private String status;    // FULLY_INDEXED, PARTIAL_INDEXED, FAILED
}
