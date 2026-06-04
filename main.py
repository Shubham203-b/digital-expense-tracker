from kivy.uix.image import Image
from PIL import Image as PILImage, ImageDraw, ImageFont
import io

def update_graph(self, user, month=None, year=None):
    self.graph_box.clear_widgets()
    
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    query = """
        SELECT category, SUM(amount), COUNT(*)
        FROM expenses
        WHERE username=?
    """
    params = [user]
    if month:
        query += " AND strftime('%m', date_added) = ?"
        params.append(month.zfill(2))
    if year:
        query += " AND strftime('%Y', date_added) = ?"
        params.append(year)
    query += " GROUP BY category"
    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    labels = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]
    counts = [row[2] for row in data]

    # Colors for the pie chart
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    # Create a new image with a white background
    img_size = 400
    img = PILImage.new('RGB', (img_size, img_size), 'white')
    draw = ImageDraw.Draw(img)
    
    # Calculate total
    total = sum(amounts)
    
    # Draw the pie chart
    start_angle = -90  # Start from top
    for i, amount in enumerate(amounts):
        # Calculate angle for this slice
        angle = (amount / total) * 360
        end_angle = start_angle + angle
        
        # Draw the slice
        draw.pieslice(
            [(50, 50), (350, 350)],
            start=start_angle,
            end=end_angle,
            fill=colors[i % len(colors)]
        )
        
        # Draw the label text
        mid_angle = start_angle + (angle / 2)
        import math
        x = 200 + 140 * math.cos(math.radians(mid_angle))
        y = 200 + 140 * math.sin(math.radians(mid_angle))
        
        # Draw text background for visibility
        label_text = f"{labels[i]}\n({counts[i]} items)"
        draw.text((x-30, y-15), label_text, fill='black')
        
        start_angle = end_angle
    
    # Save to memory buffer
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    # Display in Kivy
    self.graph_box.add_widget(Image(source=buf, size_hint=(1, 1)))
