package com.merbancapital.backend.model;

import com.merbancapital.backend.security.UserPrincipal;
import jakarta.persistence.*;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.*;
import java.util.stream.Collectors;

@Entity
@Table(name = "users")
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    // This ties a user to a department (for department-scoped users)
    @Column(name = "department_id")
    private Integer departmentId;

    @ManyToMany(fetch = FetchType.EAGER)
    @JoinTable(
            name = "user_roles",
            joinColumns = @JoinColumn(name = "user_id"),
            inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();

    public User() {
        // Default constructor for JPA
    }
    public User(String username, String email, String encode, Integer departmentId) {
        this.username = username;
        this.email = email;
        this.password = encode; // Assume encode is a pre-encoded password
        this.departmentId = departmentId != null ? departmentId.intValue() : null; // Convert Long to Integer
    }

    // --- getters & setters for all fields ---

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    @Override
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    @Override
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public Integer getDepartmentId() { return departmentId; }
    public void setDepartmentId(Integer departmentId) { this.departmentId = departmentId; }

    public Set<Role> getRoles() { return roles; }
    public void setRoles(Set<Role> roles) { this.roles = roles; }

    // Setters for UserPrincipal compatibility
    public void setDepartmentId(int departmentId) { this.departmentId = departmentId; }

    // --- UserDetails methods below ---

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return roles.stream()
                .map(r -> new SimpleGrantedAuthority(r.getName()))
                .collect(Collectors.toList());
    }

    @Override
    public boolean isAccountNonExpired() { return true; }

    @Override
    public boolean isAccountNonLocked() { return true; }

    @Override
    public boolean isCredentialsNonExpired() { return true; }

    @Override
    public boolean isEnabled() { return true; }


    public boolean isLocked() {
        // Custom logic to determine if the user is locked
        // For example, you might check a "locked" field in the database
        return false; // Default to not locked
    }

    public void setRole(Role role) {
        if (this.roles == null) {
            this.roles = new HashSet<>();
        }
        this.roles.add(role);
    }

    public void setDepartment(Department dept) {
        if (dept != null) {
            this.departmentId = dept.getDepartmentId();
        } else {
            this.departmentId = null; // Clear department if null
        }
    }
}
