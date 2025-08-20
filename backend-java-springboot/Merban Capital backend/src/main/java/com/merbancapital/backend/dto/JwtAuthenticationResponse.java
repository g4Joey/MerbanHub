// JwtAuthenticationResponse.java
package com.merbancapital.backend.dto;
import jakarta.validation.constraints.NotBlank;

public class JwtAuthenticationResponse {

        @NotBlank(message = "Access token cannot be blank")
        private String accessToken;

        @NotBlank(message = "Token type cannot be blank")
        private String tokenType = "Bearer";

        public JwtAuthenticationResponse(String token) {
            this.accessToken = token;
        }

    // getters
    public String getAccessToken() { return accessToken; }
    public String getTokenType()   { return tokenType; }
}
