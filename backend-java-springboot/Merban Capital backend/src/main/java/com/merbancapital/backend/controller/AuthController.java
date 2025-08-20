package com.merbancapital.backend.controller;

import com.merbancapital.backend.model.Role;
import com.merbancapital.backend.model.User;
import com.merbancapital.backend.dto.JwtResponse;
import com.merbancapital.backend.dto.LoginRequest;
import com.merbancapital.backend.dto.SignupRequest;
import com.merbancapital.backend.repository.RoleRepository;
import com.merbancapital.backend.repository.UserRepository;
import com.merbancapital.backend.security.JwtTokenProvider;
import com.merbancapital.backend.security.UserPrincipal;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import jakarta.validation.Valid;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {

    @Autowired AuthenticationManager authenticationManager;
    @Autowired UserRepository userRepository;
    @Autowired RoleRepository roleRepository;
    @Autowired PasswordEncoder passwordEncoder;
    @Autowired JwtTokenProvider tokenProvider;

    @PostMapping("/login")
    public ResponseEntity<JwtResponse> authenticateUser(@Valid @RequestBody LoginRequest loginRequest) {
        Authentication auth = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        loginRequest.getUsername(),
                        loginRequest.getPassword()
                )
        );
        SecurityContextHolder.getContext().setAuthentication(auth);

        UserPrincipal principal = (UserPrincipal) auth.getPrincipal();
        String jwt = tokenProvider.generateToken(principal);

        User user = userRepository.findByUsername(loginRequest.getUsername()).get();
        return ResponseEntity.ok(new JwtResponse(
                jwt,
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                auth.getAuthorities().stream()
                        .map(a -> new Role(a.getAuthority()))
                        .collect(Collectors.toSet())
    ));
}

    @PostMapping("/signup")
    public ResponseEntity<?> registerUser(@Valid @RequestBody SignupRequest signUp) {
        if (userRepository.existsByUsername(signUp.getUsername())) {
            return ResponseEntity
                    .badRequest()
                    .body("Error: Username is already taken!");
        }
        if (userRepository.existsByEmail(signUp.getEmail())) {
            return ResponseEntity
                    .badRequest()
                    .body("Error: Email is already in use!");
        }

        // Create user
        User user = new User(
                signUp.getUsername(),
                signUp.getEmail(),
                passwordEncoder.encode(signUp.getPassword()),
                signUp.getDepartmentId()
        );

        // Assign roles
        Set<Role> roles = new HashSet<>();
        for (String r : signUp.getRoles()) {
            Role role = roleRepository.findByName(r)
                    .orElseThrow(() -> new RuntimeException("Error: Role " + r + " not found."));
            roles.add(role);
        }
        user.setRoles(roles);

        userRepository.save(user);
        return ResponseEntity.ok("User registered successfully");
    }
}