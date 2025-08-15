// JwtTokenProvider.java
package com.merbancapital.backend.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

@Component
public class JwtTokenProvider {

    private final String jwtSecret;       // injected from properties
    private final long jwtExpirationMs;   // injected from properties

    public JwtTokenProvider(
            @Value("${jwt.secret}") String jwtSecret,
            @Value("${jwt.expiration-ms}") long jwtExpirationMs) {
        this.jwtSecret = jwtSecret;
        this.jwtExpirationMs = jwtExpirationMs;
    }

    // Use a secure key for HS512 (>= 64 bytes)
    private SecretKey getSigningKey() {
        byte[] keyBytes;
        try {
            // Prefer Base64-encoded secret in env
            keyBytes = Decoders.BASE64.decode(jwtSecret);
        } catch (IllegalArgumentException ignore) {
            // Fallback to raw bytes if not Base64
            keyBytes = jwtSecret.getBytes(StandardCharsets.UTF_8);
        }
        // Throws WeakKeyException if key is too small for HS512
        return Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateToken(UserPrincipal principal) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtExpirationMs);

        return Jwts.builder()
                .setSubject(principal.getUsername()) // subject = username
                .claim("uid", principal.getId())      // numeric user id
                .claim("roles", principal.getRoles())
                .claim("departmentId", principal.getDepartmentId())
                .setIssuedAt(now)
                .setExpiration(expiry)
                .signWith(getSigningKey(), SignatureAlgorithm.HS512)
                .compact();
    }

    private Jws<Claims> parse(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token);
    }

    public Long getUserIdFromJWT(String token) {
        Claims claims = parse(token).getBody();
        Number uid = claims.get("uid", Number.class);
        if (uid == null) {
            // Fallback in case older tokens used subject as ID (optional)
            String sub = claims.getSubject();
            try {
                return Long.parseLong(sub);
            } catch (NumberFormatException e) {
                throw new IllegalStateException("Token does not contain a numeric user id", e);
            }
        }
        return uid.longValue();
    }

    public boolean validateToken(String authToken) {
        try {
            parse(authToken);
            return true;
        } catch (JwtException | IllegalArgumentException ex) {
            // invalid JWT
            return false;
        }
    }

    public Claims getClaims(String jwt) {
        try {
            return parse(jwt).getBody();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    public String getUsernameFromToken(String token) {
        try {
            Claims claims = parse(token).getBody();
            return claims.getSubject(); // subject is the username
        } catch (JwtException e) {
            throw new SecurityException("Invalid JWT token", e);
        }
    }
}