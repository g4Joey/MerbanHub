package com.merbancapital.backend.dto;

import com.merbancapital.backend.model.Role;
import jakarta.validation.constraints.*;

import java.util.Set;

public class JwtResponse {
    @NotNull(message = "Token cannot be null")
    private String token;

    @NotNull(message = "Token type cannot be null")
    private String type = "Bearer";

    @NotNull(message = "User ID cannot be null")
    private Integer id;

    @NotBlank(message = "Username cannot be blank")
    @Size(min = 3, max = 20, message = "Username must be between 3 and 20 characters")
    private String username;

    @NotBlank(message = "Email cannot be blank")
    @Email(message = "Email should be valid")
    private String email;

    @NotEmpty(message = "Roles cannot be empty")
    private Set<Role> roles;

    public JwtResponse(String token, Integer id, String username, String email, Set<Role> roles) {
        this.token = token;
        this.id = id;
        this.username = username;
        this.email = email;
        this.roles = roles;
    }

    // getters only (no setters)
    public String getToken() { return token; }
    public String getType() { return type; }
    public Integer getId() { return id; }
    public String getUsername() { return username; }
    public String getEmail() { return email; }
    public Set<Role> getRoles() { return roles; }
}
