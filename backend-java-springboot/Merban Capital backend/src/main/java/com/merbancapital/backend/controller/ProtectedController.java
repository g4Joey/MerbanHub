package com.merbancapital.backend.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

// This controller is meant to demonstrate protected endpoints and role-based access control.

@RestController
@RequestMapping("/api/protected")
public class ProtectedController {

    // Anyone with a valid JWT (any role) can access this
    @GetMapping("/ping")
    public Map<String, Object> ping(Authentication auth) {
        Map<String, Object> resp = new HashMap<>();
        resp.put("ok", true);
        resp.put("user", auth.getName());
        resp.put("authorities", auth.getAuthorities().stream()
                .map(a -> a.getAuthority())
                .collect(Collectors.toList()));
        return resp;
    }

    // Example of role-restricted endpoint: requires ROLE_ADMIN or ROLE_USER
    @PreAuthorize("hasAnyRole('ADMIN','USER')")
    @GetMapping("/whoami")
    public Map<String, Object> whoami(Authentication auth) {
        Map<String, Object> resp = new HashMap<>();
        resp.put("username", auth.getName());
        return resp;
    }
}