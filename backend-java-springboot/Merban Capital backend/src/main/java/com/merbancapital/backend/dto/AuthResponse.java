package com.merbancapital.backend.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthResponse {
    @NonNull
    private String token;       // JWT token to be returned on successful login

    @NonNull
    private String username;    // Echo the username back if needed

    @NonNull
    private String role;        // User role (e.g., USER, ADMIN)
}