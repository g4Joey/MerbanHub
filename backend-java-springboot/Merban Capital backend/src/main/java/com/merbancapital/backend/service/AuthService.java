package com.merbancapital.backend.service;

import com.merbancapital.backend.dto.*;
import com.merbancapital.backend.model.*;
import com.merbancapital.backend.repository.*;
import com.merbancapital.backend.security.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.*;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    @Autowired private AuthenticationManager authenticationManager;
    @Autowired private UserRepository userRepository;
    @Autowired private RoleRepository roleRepository;
    @Autowired private DepartmentRepository departmentRepository;
    @Autowired private PasswordEncoder passwordEncoder;
    @Autowired private JwtTokenProvider tokenProvider;

    public void registerUser(com.merbancapital.backend.dto.SignupRequest req) {
        if (userRepository.existsByUsername(req.getUsername())) {
            throw new IllegalArgumentException("Username already taken");
        }
        Role role = roleRepository.findByName(req.getRoles().toString())
                .orElseThrow(() -> new IllegalArgumentException("Invalid role: " + req.getRoles()));
        Department dept = departmentRepository.findById(Long.valueOf(req.getDepartmentId()))
                .orElseThrow(() -> new IllegalArgumentException("Invalid department ID"));

        User user = new User();
        user.setUsername(req.getUsername());
        user.setPassword(passwordEncoder.encode(req.getPassword()));
        user.setRole(role);
        user.setDepartment(dept);

        userRepository.save(user);
    }

    public JwtAuthenticationResponse authenticateUser(com.merbancapital.backend.dto.LoginRequest req) {
        Authentication auth = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        req.getUsername(), req.getPassword()
                )
        );
        UserPrincipal principal = (UserPrincipal) auth.getPrincipal();
        String token = tokenProvider.generateToken(principal);
        return new JwtAuthenticationResponse(token);
    }
}
